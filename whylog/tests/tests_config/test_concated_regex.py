from unittest import TestCase

import six

from whylog.config import RegexParserFactory
from whylog.config.parsers import ConcatenatedRegexParser
from whylog.teacher.user_intent import UserParserIntent

# convertions
to_date = "date"


class TestConcatedRegexParser(TestCase):
    def setUp(self):
        self.connection_error_line = "2015-12-03 12:08:09 Connection error occurred on alfa36. Host name: 2"
        self.data_migration_line = "2015-12-03 12:10:10 Data migration from alfa36 to alfa21 failed. Host name: 2"
        self.lost_data_line = "2015-12-03 12:11:00 Data is missing at alfa21. Loss = 567.02 GB. Host name: 101"
        self.root_cause_line = "root cause"

        regex1 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Connection error occurred on (.*)\. Host name: (.*)$"
        regex2 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data migration from (.*) to (.*) failed\. Host name: (.*)$"
        regex3 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)\. Loss = (.*) GB\. Host name: (.*)$"
        regex4 = "^root cause$"
        regex5 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing"
        regex6 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)$"
        regex7 = "^dummy regex"

        parser_intent1 = UserParserIntent("connectionerror", "hydra", regex1, [1], {1: to_date})
        parser_intent2 = UserParserIntent("datamigration", "hydra", regex2, [1], {1: to_date})
        parser_intent3 = UserParserIntent("lostdata", "filesystem", regex3, [1], {1: to_date})
        parser_intent4 = UserParserIntent("rootcause", "filesystem", regex4, [], {})
        parser_intent5 = UserParserIntent("date", "filesystem", regex5, [1], {1: to_date})
        parser_intent6 = UserParserIntent("onlymissdata", "filesystem", regex6, [1], {1: to_date})
        parser_intent7 = UserParserIntent("dummy", "filesystem", regex7, [], {1: to_date})

        self.connection_error = RegexParserFactory.create_from_intent(parser_intent1)
        self.data_migration = RegexParserFactory.create_from_intent(parser_intent2)
        self.lost_data = RegexParserFactory.create_from_intent(parser_intent3)
        self.root_cause = RegexParserFactory.create_from_intent(parser_intent4)
        self.lost_data_date = RegexParserFactory.create_from_intent(parser_intent5)
        self.lost_data_suffix = RegexParserFactory.create_from_intent(parser_intent6)
        self.dummy_parser = RegexParserFactory.create_from_intent(parser_intent7)

    def test_common_cases(self):
        concatenated = ConcatenatedRegexParser(
            [
                self.connection_error, self.data_migration, self.lost_data, self.root_cause,
                self.lost_data_date, self.lost_data_suffix
            ]
        )

        assert concatenated.get_extracted_regex_params("aaaaa") == {}

        assert concatenated.get_extracted_regex_params(self.connection_error_line) == {
            self.connection_error.name: (
                "2015-12-03 12:08:09", "alfa36", "2"
            )
        }

        assert concatenated.get_extracted_regex_params(self.data_migration_line) == {
            self.data_migration.name: (
                "2015-12-03 12:10:10", "alfa36", "alfa21", "2"
            )
        }

        assert concatenated.get_extracted_regex_params(self.lost_data_line) == {
            self.lost_data.name: ("2015-12-03 12:11:00", "alfa21", "567.02", "101"),
            self.lost_data_date.name: ("2015-12-03 12:11:00",),
            self.lost_data_suffix.name:
            ("2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"),
        }

        assert concatenated.get_extracted_regex_params(self.root_cause_line) == {
            self.root_cause.name: ()
        }

    def test_all_subregexes_matches(self):
        concatenated = ConcatenatedRegexParser(
            [
                self.lost_data, self.lost_data_suffix, self.lost_data_date
            ]
        )

        assert concatenated.get_extracted_regex_params(self.lost_data_line) == {
            self.lost_data.name: ("2015-12-03 12:11:00", "alfa21", "567.02", "101"),
            self.lost_data_suffix.name:
            ("2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"),
            self.lost_data_date.name: ("2015-12-03 12:11:00",),
        }

    def test_matches_first_and_last_and_one_in_middle(self):
        concatenated = ConcatenatedRegexParser(
            [
                self.lost_data, self.dummy_parser, self.dummy_parser, self.lost_data_suffix,
                self.dummy_parser, self.dummy_parser, self.lost_data_date
            ]
        )

        assert concatenated.get_extracted_regex_params(self.lost_data_line) == {
            self.lost_data.name: ("2015-12-03 12:11:00", "alfa21", "567.02", "101"),
            self.lost_data_suffix.name:
            ("2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"),
            self.lost_data_date.name: ("2015-12-03 12:11:00",),
        }

    def test_matches_first_and_second_and_reverse(self):
        concatenated = ConcatenatedRegexParser(
            [
                self.lost_data, self.lost_data_suffix, self.connection_error, self.data_migration
            ]
        )

        assert concatenated.get_extracted_regex_params(self.lost_data_line) == {
            self.lost_data.name: ("2015-12-03 12:11:00", "alfa21", "567.02", "101"),
            self.lost_data_suffix.name:
            ("2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"),
        }

        concatenated = ConcatenatedRegexParser(
            [
                self.data_migration, self.connection_error, self.lost_data_suffix, self.lost_data
            ]
        )

        assert concatenated.get_extracted_regex_params(self.lost_data_line) == {
            self.lost_data.name: ("2015-12-03 12:11:00", "alfa21", "567.02", "101"),
            self.lost_data_suffix.name:
            ("2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"),
        }

    def test_single_subregex(self):
        concatenated = ConcatenatedRegexParser([self.lost_data])

        assert concatenated.get_extracted_regex_params(self.lost_data_line) == {
            self.lost_data.name: ("2015-12-03 12:11:00", "alfa21", "567.02", "101"),
        }

        concatenated = ConcatenatedRegexParser([self.lost_data_suffix])

        assert concatenated.get_extracted_regex_params(self.lost_data_line) == {
            self.lost_data_suffix.name:
            ("2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"),
        }

    def get_no_lost_data_parser_list(self):
        size = 100
        base_list = []
        for i in six.moves.range(size):
            if i % 2 == 0:
                parser = self.connection_error
            else:
                parser = self.data_migration
            base_list.append(parser)
        return base_list

    def test_large_matches_first_and_second(self):
        concatenated = ConcatenatedRegexParser(
            [self.lost_data, self.lost_data_suffix] + self.get_no_lost_data_parser_list()
        )

        assert concatenated.get_extracted_regex_params(self.lost_data_line) == {
            self.lost_data.name: ("2015-12-03 12:11:00", "alfa21", "567.02", "101"),
            self.lost_data_suffix.name:
            ("2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"),
        }

    def test_large_matches_first_second_and_last(self):
        concatenated = ConcatenatedRegexParser(
            [self.lost_data, self.lost_data_suffix] + self.get_no_lost_data_parser_list(
            ) + [self.lost_data_date]
        )

        assert concatenated.get_extracted_regex_params(self.lost_data_line) == {
            self.lost_data.name: ("2015-12-03 12:11:00", "alfa21", "567.02", "101"),
            self.lost_data_suffix.name:
            ("2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"),
            self.lost_data_date.name: ("2015-12-03 12:11:00",),
        }

    def test_large_matches_first_and_last_two(self):
        concatenated = ConcatenatedRegexParser(
            [self.lost_data_suffix] + self.get_no_lost_data_parser_list() + [
                self.lost_data, self.lost_data_date
            ]
        )

        assert concatenated.get_extracted_regex_params(self.lost_data_line) == {
            self.lost_data.name: ("2015-12-03 12:11:00", "alfa21", "567.02", "101"),
            self.lost_data_suffix.name:
            ("2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"),
            self.lost_data_date.name: ("2015-12-03 12:11:00",),
        }
