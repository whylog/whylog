from datetime import datetime
from unittest import TestCase

from whylog.config.parser_subset import ConcatenatedRegexParser
from whylog.config.parsers import RegexParser
from whylog.converters.exceptions import UnsupportedConverterError


class TestBasic(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser_name = 'commited_transaction'
        cls.simple_pattern = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Commited transaction number (.*)\. Host name: (.*)$"
        cls.simple_line = "2015-12-03 12:10:10 Commited transaction number 2100. Host name: postgres_db"
        cls.dummy_line = "dummy line"

    def test_simple_convertion(self):
        convertions = {1: 'date', 2: 'int', 3: 'string'}
        parser = RegexParser(
            self.parser_name, self.simple_line, self.simple_pattern, [1], 'default', convertions
        )
        concatenated = ConcatenatedRegexParser([parser])
        assert concatenated.convert_parsers_groups_from_matched_line(self.simple_line) == {
            'commited_transaction': (datetime(2015, 12, 3, 12, 10, 10), 2100, 'postgres_db')
        }
        assert concatenated.convert_parsers_groups_from_matched_line(self.dummy_line) == {}

    def test_unsupported_converter(self):
        convertions = {1: 'date', 2: 'int', 3: 'unsupported_type'}
        parser = RegexParser(
            self.parser_name, self.simple_line, self.simple_pattern, [1], 'default', convertions
        )
        concatenated = ConcatenatedRegexParser([parser])
        self.assertRaises(
            UnsupportedConverterError, concatenated.convert_parsers_groups_from_matched_line,
            self.simple_line
        )
