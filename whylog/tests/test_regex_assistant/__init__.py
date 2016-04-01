import re
from unittest import TestCase

from whylog.assistant.regex_assistant import RegexAssistant
from whylog.assistant.regex_assistant.regex import (
    NotMatchingRegexError, create_date_regex, create_obvious_regex, verify_regex
)
from whylog.assistant.span import sort_by_start
from whylog.assistant.spans_finding import (
    _find_date_spans_by_force, _find_spans_by_regex, find_date_spans
)
from whylog.front import FrontInput


class TestBasic(TestCase):
    def test_verify_regex(self):
        line = r"2015-12-03 12:11:00 Data is missing on comp21"
        regex = r"^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing on (.*)$"
        matched, groups, errors = verify_regex(regex, line)
        assert (matched, len(groups), len(errors)) == (True, 2, 0)
        assert groups[0] == r"2015-12-03 12:11:00"
        assert groups[1] == r"comp21"

        line2 = r"2015-12-03 12:11:00 Data is missing"
        matched, groups, errors = verify_regex(regex, line2)
        assert (matched, len(groups), len(errors)) == (False, 0, 1)
        assert isinstance(errors[0], NotMatchingRegexError)

    def test_create_obvious_regex(self):
        line = r".^$*x+x{5}?\*[x]x|y(x)(?iLmsux)(?:x)(?P<name>x)(?#x)(?<!x)\4\b\A"
        obvious_regex = create_obvious_regex(line)
        assert obvious_regex == \
               r"\.\^\$\*x\+x\{5\}\?\\\*\[x\]x\|y\(x\)\(\?iLmsux\)\(\?:x\)\(\?P<name>x\)\(\?#x\)\(\?<!x\)\\4\\b\\A"
        matched, groups, errors = verify_regex(obvious_regex, line)
        assert (matched, len(groups), len(errors)) == (True, 0, 0)

    def test_create_date_regex(self):
        date = '10/Oct/1999:21:15:05'
        regex = create_date_regex(date)
        matched, groups, errors = verify_regex(regex, date)
        assert (matched, len(groups), len(errors)) == (True, 0, 0)
        bad_dates = [
            date + " ", date + ":", "1" + date, '10/10/1999:21:15:05', '10/Oct/199:21:15:05',
            '10/Oct1/1999:21:15:05', '10/Oct/1999:21:15:05PM', '10/Oct/1999:021:15:05',
            '10\Oct\1999:21:15:05'
        ]
        for bad_date in bad_dates:
            assert verify_regex(regex, bad_date)[0] is False

        ok_dates = [
            '1/Oct/1999:21:15:05', '10/October/1999:21:15:05', '10/Octyyy/1999:21:15:05',
            '10/O/1999:21:15:05', '1/Oct/1999:2:1:0'
        ]
        for ok_date in ok_dates:
            assert verify_regex(regex, ok_date)[0] is True

    def test_find_spans_by_regex(self):
        date_regex = r"\d+-\d+-\d\d"
        object_regex = r"comp\d\d"
        raw_regexes = {date_regex, object_regex}
        regexes = {re.compile(regex): regex for regex in raw_regexes}

        text = r"2015-12-03 Data migration from comp36 to comp21 failed"
        spans = _find_spans_by_regex(regexes, text)
        assert len(spans) == 3
        spans = sort_by_start(spans)
        groups = [text[s.start:s.end] for s in spans]
        assert groups[0] == '2015-12-03'
        assert groups[1] == 'comp36'
        assert groups[2] == 'comp21'

    def test_find_date_spans_by_force(self):
        text = r'2015-12-03 or [10/Oct/1999:21:15:05 +0500] "GET /index.html HTTP/1.0" 200 1043'
        spans = _find_date_spans_by_force(text)
        assert len(spans) == 3
        spans = sort_by_start(spans)
        dates = [text[s.start:s.end] for s in spans]
        assert dates[0] == '2015-12-03'
        assert dates[1] == '10/Oct/1999'
        assert dates[2] == '21:15:05 +0500'

    def test_find_date_spans(self):
        raw_date_regexes = {r"\d+/[a-zA-z]+/\d+:\d+:\d+:\d+ \+\d+"}
        date_regexes = {re.compile(regex): regex for regex in raw_date_regexes}

        text = r'2015-12-03 or [10/Oct/1999:21:15:05 +0500] "GET /index.html HTTP/1.0" 200 1043'
        spans = find_date_spans(text, date_regexes)
        assert len(spans) == 2
        spans = sort_by_start(spans)
        dates = [text[s.start:s.end] for s in spans]
        assert dates[0] == '2015-12-03'
        assert dates[1] == '10/Oct/1999:21:15:05 +0500'




