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

        id_to_line_dict = {1: cause1, 2: cause2, 3: effect}

        regex_assistant = RegexAssistant()
        regex_assistant.add_lines(id_to_line_dict)

        regex_assistant.remove_lines([3])
        assert len(regex_assistant.regexes) == 2

        regex_assistant.add_lines({3: effect})
        assert len(regex_assistant.regexes) == 3

        assert regex_assistant.regexes[2] == '^' + content2 + '$'

        beta36_in_1 = Interval(49, 54, 1)
        beta36_in_2 = Interval(40, 45, 1)

        raise SkipTest
        # Methods called below are not implemented yet.
        regex_assistant.make_groups([beta36_in_1, beta36_in_2])
        assert regex_assistant.regexes[
            1
        ] == "^2015-12-03 12:08:09 Connection error occurred on (.*)$"
        assert regex_assistant.regexes[
            2
        ] == "^2015-12-03 12:10:10 Data migration from (.*) to beta21 failed$"

        regex_assistant.guess_regex(3)
        assert regex_assistant.regexes[
            3
        ] == "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing on (.*)$"

        proposed_regex = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing on (beta.*)$"
        regex_assistant.update_regex(3, proposed_regex)
        assert regex_assistant.regexes[3] == proposed_regex

        with self.assertRaises(NoDateGroupException):
            regex_assistant.verify_regex(1)
