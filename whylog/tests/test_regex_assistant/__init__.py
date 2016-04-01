import re
from unittest import TestCase

from whylog.assistant.regex_assistant import RegexAssistant
from whylog.assistant.regex_assistant.regex import (
    NotMatchingRegexError, create_date_regex, create_obvious_regex, verify_regex
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









