import re
from unittest import TestCase

from whylog.assistant.regex_assistant import RegexAssistant
from whylog.assistant.regex_assistant.exceptions import NotMatchingRegexError
from whylog.assistant.regex_assistant.regex import (
    create_date_regex, create_obvious_regex, group_spans_from_regex, regex_from_group_spans,
    verify_regex
)
from whylog.assistant.span_list import SpanList
from whylog.assistant.spans_finding import (
    _find_date_spans_by_force, find_spans_by_regex, find_date_spans
)
from whylog.front.utils import FrontInput


class TestBasic(TestCase):
    def _verify_regex_success(self, regex, line, wanted_groups=None):
        try:
            groups = verify_regex(regex, line)
            if wanted_groups is not None:
                assert groups == wanted_groups
        except NotMatchingRegexError as e:
            self.fail(e)

    def _verify_regex_fail(self, regex, line):
        self.assertRaises(NotMatchingRegexError, verify_regex, regex, line)

    def test_verify_regex_success(self):
        line = r"2015-12-03 12:11:00 Data is missing on comp21"
        regex = r"^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing on (.*)$"
        self._verify_regex_success(regex, line, ('2015-12-03 12:11:00', 'comp21'))

    def test_verify_regex_fail(self):
        line = r"2015-12-03 12:11:00 Data is missing"
        regex = r"^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing on (.*)$"
        self._verify_regex_fail(regex, line)

    def test_create_obvious_regex(self):
        line = r".^$*x+x{5}?\*[x]x|y(x)(?iLmsux)(?:x)(?P<name>x)(?#x)(?<!x)\4\b\A"
        obvious_regex = create_obvious_regex(line)
        assert (
            obvious_regex == r"\.\^\$\*x\+x\{5\}\?\\\*\[x\]x\|y\(x\)\(\?iLmsux\)\(\?:x\)"
            r"\(\?P<name>x\)\(\?#x\)\(\?<!x\)\\4\\b\\A"
        )

        self._verify_regex_success(obvious_regex, line, ())

    def test_create_date_regex(self):
        date = '10/Oct/1999:21:15:05'
        regex = create_date_regex(date)
        self._verify_regex_success(regex, date, ())

        not_matching_dates = [
            date + " ", date + ":", "1" + date, '10/10/1999:21:15:05', '10/Oct/199:21:15:05',
            '10/Oct1/1999:21:15:05', '10/Oct/1999:21:15:05PM', '10/Oct/1999:021:15:05',
            '10\Oct\1999:21:15:05'
        ]
        for not_matching_date in not_matching_dates:
            self._verify_regex_fail(regex, not_matching_date)

        matching_dates = [
            '1/Oct/1999:21:15:05', '10/October/1999:21:15:05', '10/Octyyy/1999:21:15:05',
            '10/O/1999:21:15:05', '1/Oct/1999:2:1:0'
        ]
        for matching_date in matching_dates:
            self._verify_regex_success(regex, matching_date)

    def test_find_spans_by_regex(self):
        regexes = dict((re.compile(regex), regex) for regex in [r"\d+-\d+-\d\d", r"comp\d\d"])
        text = r"2015-12-03 Data migration from comp36 to comp21 failed"
        spans = find_spans_by_regex(regexes, text)
        assert len(spans) == 3
        spans = SpanList(spans).sort_by_start_and_end()
        groups = [text[s.start:s.end] for s in spans]
        assert groups[0] == '2015-12-03'
        assert groups[1] == 'comp36'
        assert groups[2] == 'comp21'

    def test_find_date_spans_by_force(self):
        text = r'2015-12-03 or [10/Oct/1999:21:15:05 +0500] "GET /index.html HTTP/1.0" 200 1043'
        spans = _find_date_spans_by_force(text)
        assert len(spans) == 3
        spans = SpanList(spans).sort_by_start_and_end()
        dates = [text[s.start:s.end] for s in spans]
        assert dates[0] == '2015-12-03'
        assert dates[1] == '10/Oct/1999'
        assert dates[2] == '21:15:05 +0500'

    def test_find_date_spans(self):
        raw_date_regex = r"\d+/[a-zA-z]+/\d+:\d+:\d+:\d+ \+\d+"
        date_regexes = {re.compile(raw_date_regex): raw_date_regex}

        text = r'2015-12-03 or [10/Oct/1999:21:15:05 +0500] "GET /index.html HTTP/1.0" 200 1043'
        spans = find_date_spans(text, date_regexes)
        assert len(spans) == 2
        spans = spans.sort_by_start_and_end()
        dates = [text[s.start:s.end] for s in spans]
        assert dates[0] == '2015-12-03'
        assert dates[1] == '10/Oct/1999:21:15:05 +0500'

    def test_guess_regex(self):
        line = r'2015-12-03 or [10/Oct/1999 21:15:05 +0500] "GET /index.html HTTP/1.0" 200 1043'
        front_input = FrontInput(0, line, 0)
        line_id = 1
        ra = RegexAssistant()
        ra.add_line(line_id, front_input)
        pattern_objects = ra.guess(line_id)
        assert pattern_objects
        guessed_regexes = [pattern_object.pattern for pattern_object in pattern_objects.values()]
        for guessed_regex in guessed_regexes:
            self._verify_regex_success(guessed_regex, line)

    def test_group_spans_from_regex(self):
        text = r'12:56:23 Error on comp12'
        regex = r'^(\d\d:\d\d:\d\d) Error on (comp(\d+))$'
        spans = group_spans_from_regex(regex, text)
        assert set([(span.start, span.end, span.pattern) for span in spans]) == set(
            [
                (0, 8, '\d\d:\d\d:\d\d'), (18, 24, 'comp(\d+)'), (22, 24, '\d+')
            ]
        )

    def test_update(self):
        ra = RegexAssistant()
        line = "Hello, Whylog guy!"
        line_id = 1
        ra.add_line(line_id, FrontInput(0, line, 0))
        unlikely_regex = r'^Hello, (Whylog (team|guy)!)$'
        assert not ra.regex_objects[line_id].regex == unlikely_regex
        ra.update(line_id, unlikely_regex)
        assert ra.regex_objects[line_id].regex == unlikely_regex

    def test_regex_from_group_spans(self):
        text = r'Error on comp21'
        regex = r'^Error on (comp(\d\d))$'
        group_spans = group_spans_from_regex(regex, text)
        regex_from_groups = regex_from_group_spans(group_spans, text)
        assert regex == regex_from_groups
