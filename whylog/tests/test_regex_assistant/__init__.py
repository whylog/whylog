from unittest import TestCase

from nose.plugins.skip import SkipTest

from whylog.assistant import RegexAssistant
from whylog.assistant.regex_assistant_exceptions import NoDateGroupException
from whylog.front import FrontInput
from whylog.teacher import Interval


class TestBasic(TestCase):
    def test_one(self):
        content1 = "2015-12-03 12:08:09 Connection error occurred on beta36"
        content2 = "2015-12-03 12:10:10 Data migration from beta36 to beta21 failed"
        content3 = "2015-12-03 12:11:00 Data is missing on beta21"

        cause1 = FrontInput(903, content1, None)
        cause2 = FrontInput(53, content2, None)
        effect = FrontInput(1087, content3, None)

        regex_assistant = RegexAssistant(effect, [cause1])

        regex_assistant.remove_lines([effect])
        assert len(regex_assistant.regexes) == 1

        regex_assistant.add_lines([cause2, effect])

        assert regex_assistant.regexes[cause2] == '^' + content2 + '$'

        beta36_in_1 = Interval(49, 54, cause1)
        beta36_in_2 = Interval(40, 45, cause2)

        raise SkipTest
        # Methods called below are not implemented yet.
        regex_assistant.make_groups([beta36_in_1, beta36_in_2])
        assert regex_assistant.regexes[
            cause1
        ] == "^2015-12-03 12:08:09 Connection error occurred on (.*)$"
        assert regex_assistant.regexes[
            cause2
        ] == "^2015-12-03 12:10:10 Data migration from (.*) to beta21 failed$"

        regex_assistant.undo(cause1)
        assert regex_assistant.regexes[cause1] == '^' + content2 + '$'
        regex_assistant.redo(cause1)
        assert regex_assistant.regexes[
            cause1
        ] == "^2015-12-03 12:08:09 Connection error occurred on (.*)$"

        regex_assistant.guess_regex(effect)
        assert regex_assistant.regexes[
            effect
        ] == "^(?P<date>\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing on (.*)$"

        proposed_regex = "^(?P<date>\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing on (?P<machine>.*)$"
        regex_assistant.load_regex(effect, proposed_regex)
        assert regex_assistant.regexes[effect] == proposed_regex

        with self.assertRaises(NoDateGroupException):
            regex_assistant.verify_regex(cause1)
