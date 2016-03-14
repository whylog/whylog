import uuid
from unittest import TestCase

import six

from whylog.config import RegexParserFactory
from whylog.config.parsers import ConcatedRegexParser
from whylog.teacher.user_intent import UserParserIntent
from whylog.tests.tests_config.consts_for_tests import *


class TestConcatedRegexParser(TestCase):
    def test_common_cases(self):

        concated = ConcatedRegexParser([parser1, parser2, parser3, parser4, parser5, parser6])

        assert concated.get_extracted_regex_params("aaaaa") == {}

        assert concated.get_extracted_regex_params(content1) == {
            parser1.name: (
                "2015-12-03 12:08:09", "alfa36", "2"
            )
        }

        assert concated.get_extracted_regex_params(content2) == {
            parser2.name: (
                "2015-12-03 12:10:10", "alfa36", "alfa21", "2"
            )
        }

        assert concated.get_extracted_regex_params(content3) == {
            parser3.name: ("2015-12-03 12:11:00", "alfa21", "567.02", "101"),
            parser5.name: ("2015-12-03 12:11:00",),
            parser6.name: ("2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"),
        }

        assert concated.get_extracted_regex_params(content4) == {parser4.name: ()}

    # def test_all_subregexes_matches(self):
    #     regex1 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)\. Loss = (.*) GB\. Host name: (.*)$"
    #     regex2 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)$"
    #     regex3 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing"
    #
    #     parser_intent1 = UserParserIntent("date", "filesystem", regex1, [1], {1: to_date})
    #     parser_intent2 = UserParserIntent("onlymissdata", "filesystem", regex2, [1], {1: to_date})
    #     parser_intent3 = UserParserIntent("lostdata", "filesystem", regex3, [1], {1: to_date})
    #
    #     parser1 = RegexParserFactory.create_from_intent(parser_intent1)
    #     parser2 = RegexParserFactory.create_from_intent(parser_intent2)
    #     parser3 = RegexParserFactory.create_from_intent(parser_intent3)
    #
    #     concated = ConcatedRegexParser([parser1, parser2, parser3])
    #
    #     content = "2015-12-03 12:11:00 Data is missing at alfa21. Loss = 567.02 GB. Host name: 101"
    #
    #     assert concated.get_extracted_regex_params(content) == {
    #         parser1.name: ["2015-12-03 12:11:00", "alfa21", "567.02", "101"],
    #         parser2.name: ["2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"],
    #         parser3.name: ["2015-12-03 12:11:00"],
    #     }
    #
    # def test_matches_first_and_last_and_one_in_middle(self):
    #     regex1 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)\. Loss = (.*) GB\. Host name: (.*)$"
    #     regex2 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)$"
    #     regex3 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing"
    #     dummy_regex = "^dummy regex"
    #
    #     parser_intent1 = UserParserIntent("date", "filesystem", regex1, [1], {1: to_date})
    #     parser_intent2 = UserParserIntent("onlymissdata", "filesystem", regex2, [1], {1: to_date})
    #     parser_intent3 = UserParserIntent("lostdata", "filesystem", regex3, [1], {1: to_date})
    #     parser_intent4 = UserParserIntent("dummy", "filesystem", dummy_regex, [], {1: to_date})
    #
    #     parser1 = RegexParserFactory.create_from_intent(parser_intent1)
    #     parser2 = RegexParserFactory.create_from_intent(parser_intent2)
    #     parser3 = RegexParserFactory.create_from_intent(parser_intent3)
    #     dummy_parser = RegexParserFactory.create_from_intent(parser_intent4)
    #
    #     concated = ConcatedRegexParser(
    #         [parser1, dummy_parser, dummy_parser, parser2, dummy_parser, dummy_parser, parser3]
    #     )
    #
    #     content = "2015-12-03 12:11:00 Data is missing at alfa21. Loss = 567.02 GB. Host name: 101"
    #
    #     assert concated.get_extracted_regex_params(content) == {
    #         parser1.name: ["2015-12-03 12:11:00", "alfa21", "567.02", "101"],
    #         parser2.name: ["2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"],
    #         parser3.name: ["2015-12-03 12:11:00"],
    #     }
    #
    # def test_matches_first_and_second_and_reverse(self):
    #     regex1 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)\. Loss = (.*) GB\. Host name: (.*)$"
    #     regex2 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)$"
    #     regex3 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Connection error occurred on (.*)\. Host name: (.*)$"
    #     regex4 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data migration from (.*) to (.*) failed\. Host name: (.*)$"
    #
    #     parser_intent1 = UserParserIntent("date", "filesystem", regex1, [1], {1: to_date})
    #     parser_intent2 = UserParserIntent("onlymissdata", "filesystem", regex2, [1], {1: to_date})
    #     parser_intent3 = UserParserIntent("connectionerror", "hydra", regex3, [1], {1: to_date})
    #     parser_intent4 = UserParserIntent("datamigration", "hydra", regex4, [1], {1: to_date})
    #
    #     parser1 = RegexParserFactory.create_from_intent(parser_intent1)
    #     parser2 = RegexParserFactory.create_from_intent(parser_intent2)
    #     parser3 = RegexParserFactory.create_from_intent(parser_intent3)
    #     parser4 = RegexParserFactory.create_from_intent(parser_intent4)
    #
    #     content = "2015-12-03 12:11:00 Data is missing at alfa21. Loss = 567.02 GB. Host name: 101"
    #
    #     concated = ConcatedRegexParser([parser1, parser2, parser3, parser4])
    #
    #     assert concated.get_extracted_regex_params(content) == {
    #         parser1.name: ["2015-12-03 12:11:00", "alfa21", "567.02", "101"],
    #         parser2.name: ["2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"],
    #     }
    #
    #     concated = ConcatedRegexParser([parser4, parser3, parser2, parser1])
    #
    #     assert concated.get_extracted_regex_params(content) == {
    #         parser1.name: ["2015-12-03 12:11:00", "alfa21", "567.02", "101"],
    #         parser2.name: ["2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"],
    #     }
    #
    # def test_single_subregex(self):
    #     regex1 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)\. Loss = (.*) GB\. Host name: (.*)$"
    #     regex2 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)$"
    #
    #     parser_intent1 = UserParserIntent("lostdata", "filesystem", regex1, [1], {1: to_date})
    #     parser_intent2 = UserParserIntent("onlymissdata", "filesystem", regex2, [1], {1: to_date})
    #
    #     parser1 = RegexParserFactory.create_from_intent(parser_intent1)
    #     parser2 = RegexParserFactory.create_from_intent(parser_intent2)
    #
    #     content = "2015-12-03 12:11:00 Data is missing at alfa21. Loss = 567.02 GB. Host name: 101"
    #
    #     concated = ConcatedRegexParser([parser1])
    #
    #     assert concated.get_extracted_regex_params(content) == {
    #         parser1.name: ["2015-12-03 12:11:00", "alfa21", "567.02", "101"],
    #     }
    #
    #     concated = ConcatedRegexParser([parser2])
    #
    #     assert concated.get_extracted_regex_params(content) == {
    #         parser2.name: ["2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"],
    #     }
    #
    # def test_large_concated_regex(self):
    #     regex1 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)\. Loss = (.*) GB\. Host name: (.*)$"
    #     regex2 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)$"
    #     regex3 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Connection error occurred on (.*)\. Host name: (.*)$"
    #     regex4 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data migration from (.*) to (.*) failed\. Host name: (.*)$"
    #
    #     size = 100
    #
    #     parser_intent1 = UserParserIntent("lostdata", "filesystem", regex1, [1], {1: to_date})
    #     parser_intent2 = UserParserIntent("onlymissdata", "filesystem", regex2, [1], {1: to_date})
    #
    #     base_list = []
    #
    #     for i in six.moves.range(size):
    #         if i % 2 == 0:
    #             base_list.append(UserParserIntent(uuid.uuid4(), "hydra", regex3, [1], {1: to_date}))
    #         else:
    #             base_list.append(UserParserIntent(uuid.uuid4(), "hydra", regex4, [1], {1: to_date}))
    #
    #     content = "2015-12-03 12:11:00 Data is missing at alfa21. Loss = 567.02 GB. Host name: 101"
    #
    #     intents_list = [parser_intent1, parser_intent2] + base_list
    #
    #     parser_list = [RegexParserFactory.create_from_intent(intent) for intent in intents_list]
    #
    #     concated = ConcatedRegexParser(parser_list)
    #
    #     assert concated.get_extracted_regex_params(content) == {
    #         "lostdata": ["2015-12-03 12:11:00", "alfa21", "567.02", "101"],
    #         "onlymissdata": ["2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"],
    #     }
    #
    #     concated = ConcatedRegexParser(list(reversed(parser_list)))
    #
    #     assert concated.get_extracted_regex_params(content) == {
    #         "lostdata": ["2015-12-03 12:11:00", "alfa21", "567.02", "101"],
    #         "onlymissdata": ["2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"],
    #     }
    #
    #     intents_list = [parser_intent1] + base_list + [parser_intent2]
    #
    #     parser_list = [RegexParserFactory.create_from_intent(intent) for intent in intents_list]
    #
    #     concated = ConcatedRegexParser(parser_list)
    #
    #     assert concated.get_extracted_regex_params(content) == {
    #         "lostdata": ["2015-12-03 12:11:00", "alfa21", "567.02", "101"],
    #         "onlymissdata": ["2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"],
    #     }
    #
    #     random.shuffle(parser_list)
    #
    #     concated = ConcatedRegexParser(parser_list)
    #
    #     assert concated.get_extracted_regex_params(content) == {
    #         "lostdata": ["2015-12-03 12:11:00", "alfa21", "567.02", "101"],
    #         "onlymissdata": ["2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"],
    #     }
    #
    #     random.shuffle(parser_list)
    #
    #     concated = ConcatedRegexParser(parser_list)
    #
    #     assert concated.get_extracted_regex_params(content) == {
    #         "lostdata": ["2015-12-03 12:11:00", "alfa21", "567.02", "101"],
    #         "onlymissdata": ["2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"],
    #     }
