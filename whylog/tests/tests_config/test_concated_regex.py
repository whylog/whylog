import itertools
from unittest import TestCase

import six

from whylog.assistant.const import AssistantType
from whylog.assistant.pattern_match import ParamGroup
from whylog.config.parser_subset import ConcatenatedRegexParser
from whylog.config.parsers import RegexParserFactory
from whylog.teacher.user_intent import UserParserIntent

# convertions
to_date = "date"
to_string = "string"
to_float = "float"


class TestConcatedRegexParser(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection_error_line = "2015-12-03 12:08:09 Connection error occurred on alfa36. Host name: 2"
        cls.data_migration_line = "2015-12-03 12:10:10 Data migration from alfa36 to alfa21 failed. Host name: 2"
        cls.lost_data_line = "2015-12-03 12:11:00 Data is missing at alfa21. Loss = 567.02 GB. Host name: 101"
        cls.root_cause_line = "root cause"
        cls.data_missing_line = "2015-12-03 12:11:00 Data is missing"
        cls.data_missing_at_line = "2015-12-03 12:11:00 Data is missing at alfa21"
        cls.dummy_line = "dummy regex"

        regex1 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Connection error occurred on (.*)\. Host name: (.*)$"
        regex2 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data migration from (.*) to (.*) failed\. Host name: (.*)$"
        regex3 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)\. Loss = (.*) GB\. Host name: (.*)$"
        regex4 = "^root cause$"
        regex5 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing"
        regex6 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)$"
        regex7 = "^dummy regex"

        date_group = ParamGroup(None, to_date)
        string_group = ParamGroup(None, to_string)
        float_group = ParamGroup(None, to_float)

        regex_type = AssistantType.REGEX

        # yapf: disable
        parser_intent1 = UserParserIntent(
            regex_type, "connectionerror", regex1, "hydra", [1], {
                1: date_group,
                2: string_group,
                3: string_group
            }, cls.connection_error_line, 1, "serwer1"
        )
        parser_intent2 = UserParserIntent(
            regex_type, "datamigration", regex2, "hydra", [1], {
                1: date_group,
                2: string_group,
                3: string_group,
                4: string_group
            }, cls.data_migration_line, 2, "serwer2"
        )
        parser_intent3 = UserParserIntent(
            regex_type, "lostdata", regex3, "filesystem", [1], {
                1: date_group,
                2: string_group,
                3: float_group,
                4: string_group
            }, cls.lost_data_line, 3, "serwer3"
        )
        parser_intent4 = UserParserIntent(
            regex_type, "rootcause", regex4, "filesystem", [], {}, cls.root_cause_line, 4, "serwer4"
        )
        parser_intent5 = UserParserIntent(
            regex_type, "date", regex5, "filesystem", [1], {1: date_group}, cls.data_missing_line,
            5, "serwer5"
        )
        parser_intent6 = UserParserIntent(
            regex_type, "onlymissdata", regex6, "filesystem", [1], {
                1: date_group,
                2: string_group
            }, cls.data_missing_at_line, 6, "serwer6"
        )
        parser_intent7 = UserParserIntent(
            regex_type, "dummy", regex7, "filesystem", [], {}, cls.dummy_line, 7, "serwer7"
        )
        # yapf: enable

        cls.connection_error = RegexParserFactory.create_from_intent(parser_intent1)
        cls.data_migration = RegexParserFactory.create_from_intent(parser_intent2)
        cls.lost_data = RegexParserFactory.create_from_intent(parser_intent3)
        cls.root_cause = RegexParserFactory.create_from_intent(parser_intent4)
        cls.lost_data_date = RegexParserFactory.create_from_intent(parser_intent5)
        cls.lost_data_suffix = RegexParserFactory.create_from_intent(parser_intent6)
        cls.dummy_parser = RegexParserFactory.create_from_intent(parser_intent7)
        cls.no_lost_data_parser_list = cls.get_no_lost_data_parser_list()

    @classmethod
    def get_no_lost_data_parser_list(cls):
        size = 100
        base_list = []
        for i in six.moves.range(size):
            if i % 2 == 0:
                parser = cls.connection_error
            else:
                parser = cls.data_migration
            base_list.append(parser)
        return base_list

    def is_three_lost_data_parsers_matched(self, concatenated):
        assert concatenated.get_extracted_parsers_params(self.lost_data_line) == {
            self.lost_data.name: ("2015-12-03 12:11:00", "alfa21", "567.02", "101"),
            self.lost_data_date.name: ("2015-12-03 12:11:00",),
            self.lost_data_suffix.name:
            ("2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"),
        }

    def is_two_lost_data_parsers_matched(self, concatenated):
        assert concatenated.get_extracted_parsers_params(self.lost_data_line) == {
            self.lost_data.name: ("2015-12-03 12:11:00", "alfa21", "567.02", "101"),
            self.lost_data_suffix.name:
            ("2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"),
        }

    def test_common_cases(self):
        concatenated = ConcatenatedRegexParser(
            [
                self.connection_error, self.data_migration, self.lost_data, self.root_cause,
                self.lost_data_date, self.lost_data_suffix
            ]
        )

        assert concatenated.get_extracted_parsers_params("aaaaa") == {}

        assert concatenated.get_extracted_parsers_params(self.connection_error_line) == {
            self.connection_error.name: ("2015-12-03 12:08:09", "alfa36", "2")
        }

        assert concatenated.get_extracted_parsers_params(self.data_migration_line) == {
            self.data_migration.name: ("2015-12-03 12:10:10", "alfa36", "alfa21", "2")
        }

        self.is_three_lost_data_parsers_matched(concatenated)

        assert concatenated.get_extracted_parsers_params(self.root_cause_line) == {
            self.root_cause.name: ()
        }

    def test_all_subregexes_matches(self):
        concatenated = ConcatenatedRegexParser(
            [
                self.lost_data, self.lost_data_suffix, self.lost_data_date
            ]
        )

        self.is_three_lost_data_parsers_matched(concatenated)

    def test_matches_first_and_last_and_one_in_middle(self):
        concatenated = ConcatenatedRegexParser(
            [
                self.lost_data, self.dummy_parser, self.dummy_parser, self.lost_data_suffix,
                self.dummy_parser, self.dummy_parser, self.lost_data_date
            ]
        )

        self.is_three_lost_data_parsers_matched(concatenated)

    def test_two_parsers_matches_permutations(self):
        for parser_list in itertools.permutations(
            [self.data_migration, self.connection_error, self.lost_data_suffix, self.lost_data], 4
        ):
            concatenated = ConcatenatedRegexParser(parser_list)
            self.is_two_lost_data_parsers_matched(concatenated)

    def test_single_subregex(self):
        concatenated = ConcatenatedRegexParser([self.lost_data])

        assert concatenated.get_extracted_parsers_params(self.lost_data_line) == {
            self.lost_data.name: ("2015-12-03 12:11:00", "alfa21", "567.02", "101"),
        }

        concatenated = ConcatenatedRegexParser([self.lost_data_suffix])

        assert concatenated.get_extracted_parsers_params(self.lost_data_line) == {
            self.lost_data_suffix.name:
            ("2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"),
        }

    def test_large_matches_first_and_second(self):
        concatenated = ConcatenatedRegexParser(
            [self.lost_data, self.lost_data_suffix] + self.no_lost_data_parser_list
        )

        self.is_two_lost_data_parsers_matched(concatenated)

    def test_large_matches_first_second_and_last(self):
        concatenated = ConcatenatedRegexParser(
            [
                self.lost_data, self.lost_data_suffix
            ] + self.no_lost_data_parser_list + [self.lost_data_date]
        )

        self.is_three_lost_data_parsers_matched(concatenated)

    def test_large_matches_first_and_last_two(self):
        concatenated = ConcatenatedRegexParser(
            [self.lost_data_suffix] + self.no_lost_data_parser_list + [
                self.lost_data, self.lost_data_date
            ]
        )

        self.is_three_lost_data_parsers_matched(concatenated)
