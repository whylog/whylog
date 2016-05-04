import re
from unittest import TestCase

from whylog.assistant.regex_assistant import RegexAssistant
from whylog.assistant.regex_assistant.exceptions import NotMatchingRegexError
from whylog.assistant.regex_assistant.regex import (
    create_date_regex, create_obvious_regex, regex_from_group_spans,
    regex_groups, verify_regex
)
from whylog.assistant.span import Span
from whylog.assistant.span_list import SpanList
from whylog.assistant.spans_finding import (
    _find_date_spans_by_force, find_date_spans, find_spans_by_regex
)
from whylog.front.utils import FrontInput


class TestBase(TestCase):
    def verify_regex_match(self, regex, line, wanted_groups=None):
        try:
            groups = regex_groups(regex, line)
            if wanted_groups is not None:
                assert groups == wanted_groups
        except NotMatchingRegexError as e:
            self.fail(e)

    def verify_regex_not_match(self, regex, line):
        self.assertRaises(NotMatchingRegexError, verify_regex, regex, line)


class TestRegexAssistant(TestBase):
    def test_guess_pattern_matches(self):
        line = r'2015-12-03 or [10/Oct/1999 21:15:05 +0500] "GET /index.html HTTP/1.0" 200 1043'
        front_input = FrontInput(0, line, 0)
        line_id = 1
        ra = RegexAssistant()
        ra.add_line(line_id, front_input)
        pattern_matches = ra.guess_pattern_matches(line_id)
        assert pattern_matches
        guessed_regexes = [pattern_match.pattern for pattern_match in pattern_matches.values()]
        for guessed_regex in guessed_regexes:
            self.verify_regex_match(guessed_regex, line)

    def test_update_by_pattern(self):
        ra = RegexAssistant()
        line = "Hello, Whylog guy!"
        line_id = 1
        ra.add_line(line_id, FrontInput(0, line, 0))
        unlikely_regex = r'^Hello, (Whylog (team|guy)!)$'
        assert not ra.regex_matches[line_id].regex == unlikely_regex
        ra.update_by_pattern(line_id, unlikely_regex)
        assert ra.regex_matches[line_id].regex == unlikely_regex


class TestBasic(TestBase):
    def test_verify_regex_success(self):
        line = r"2015-12-03 12:11:00 Data is missing on comp21"
        regex = r"^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing on (.*)$"
        self.verify_regex_match(regex, line, ('2015-12-03 12:11:00', 'comp21'))

    def test_verify_regex_fail(self):
        line = r"2015-12-03 12:11:00 Data is missing"
        regex = r"^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing on (.*)$"
        self.verify_regex_not_match(regex, line)

    def test_create_obvious_regex(self):
        line = r".^$*x+x{5}?\*[x]x|y(x)(?iLmsux)(?:x)(?P<name>x)(?#x)(?<!x)\4\b\A"
        obvious_regex = create_obvious_regex(line)
        assert (
            obvious_regex == r"\.\^\$\*x\+x\{5\}\?\\\*\[x\]x\|y\(x\)\(\?iLmsux\)\(\?:x\)"
            r"\(\?P<name>x\)\(\?#x\)\(\?<!x\)\\4\\b\\A"
        )

        self.verify_regex_match(obvious_regex, line, ())

    def test_create_date_regex(self):
        date = '10/Oct/1999:21:15:05'
        regex = create_date_regex(date)
        self.verify_regex_match(regex, date, ())

        not_matching_dates = [
            date + " ", date + ":", "1" + date, '10/10/1999:21:15:05', '10/Oct/199:21:15:05',
            '10/Oct1/1999:21:15:05', '10/Oct/1999:21:15:05PM', '10/Oct/1999:021:15:05',
            '10\Oct\1999:21:15:05'
        ]
        for not_matching_date in not_matching_dates:
            self.verify_regex_not_match(regex, not_matching_date)

        matching_dates = [
            '1/Oct/1999:21:15:05', '10/October/1999:21:15:05', '10/Octyyy/1999:21:15:05',
            '10/O/1999:21:15:05', '1/Oct/1999:2:1:0'
        ]
        for matching_date in matching_dates:
            self.verify_regex_match(regex, matching_date)

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

    def test_regex_from_group_spans(self):
        text = r'Error on comp21'
        regex = r'^Error on (comp(\d\d))$'
        span_comp = Span(9, 15, pattern=r'comp(\d\d)')
        span_number = Span(13, 15, pattern=r'\d\d')
        group_spans = SpanList([span_comp, span_number])
        regex_from_groups = regex_from_group_spans(group_spans, text)
        assert regex == regex_from_groups
