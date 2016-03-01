from unittest import TestCase
from os.path import join as path_join
from nose.plugins.skip import SkipTest
#raise SkipTest()
from whylog.regexassistant import RegexAssistant
from whylog.teacher import Interval

class FrontInput(object):
    """
    FrontInput for test purpose only while module Front is not implemented yet.
    """
    def __init__(self, offset, line_content, resource_location):
        self.offset = offset
        self.line_content = line_content
        self.resource_location = resource_location

class TestBasic(TestCase):

    def test_one(self):
        content1 = "2015-12-03 12:08:09 Connection error occurred on beta36"
        content2 = "2015-12-03 12:10:10 Data migration from beta36 to beta21 failed"
        content3 = "2015-12-03 12:11:00 Data is missing at beta21"

        cause1 = FrontInput(903, content1, None)
        cause2 = FrontInput(53, content2, None)
        effect = FrontInput(1087, content3, None)

        regex_assistant = RegexAssistant([cause1, effect])

        regex_assistant.remove_lines([effect])
        assert len(regex_assistant.regexes) == 1

        regex_assistant.add_lines([cause2, effect])
        assert len(regex_assistant.history) == 3

        print regex_assistant.regexes[cause2]
        assert regex_assistant.regexes[cause2] == '^' + content2 + '$'

        assert 'beta36' == content1[49:55]
        assert 'beta36' == content2[40:46]
        beta36_in_1 = Interval(49, 54, cause1)
        beta36_in_2 = Interval(40, 45, cause2)

        raise SkipTest
        # Not implemented yet.
        regex_assistant.make_groups([beta36_in_1, beta36_in_2])
        assert regex_assistant.regexes[cause1] == "^2015-12-03 12:08:09 Connection error occurred on (.*)$"
        assert regex_assistant.regexes[cause2] == "^2015-12-03 12:10:10 Data migration from (.*) to beta21 failed$"

        regex_assistant.undo(cause1)
        assert regex_assistant.regexes[cause1] == '^' + content2 + '$'
        regex_assistant.redo(cause1)
        assert regex_assistant.regexes[cause1] == "^2015-12-03 12:08:09 Connection error occurred on (.*)$"

        regex_assistant.guess_regex(effect)
        assert regex_assistant.regexes[effect] == "^(?P<date>\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)$"

        proposed_regex = "^(?P<date>\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (?P<machine>.*)$"
        regex_assistant.load_regex(effect, proposed_regex)
        assert regex_assistant.regexes[effect] == proposed_regex

        error_occured = False
        try:
            regex_assistant.verify_regex(cause1)
        except NoDateGroupError:
            error_occured = True
        assert error_occured
