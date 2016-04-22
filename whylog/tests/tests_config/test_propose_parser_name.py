import os.path
from unittest import TestCase

from whylog.config import YamlConfig

path_test_files = ['whylog', 'tests', 'tests_config', 'test_files']


class TestBasic(TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.path.join(*path_test_files)
        parsers_path = os.path.join(path, 'parsers.yaml')
        rules_path = os.path.join(path, 'rules.yaml')
        log_type_path = os.path.join(path, 'log_types.yaml')

        cls.sample_line1 = "2016-04-12 23:54:45 Connection error occurred on comp1. Host name: host1"
        cls.sample_line2 = "2016-04-12 23:54:45 comp1 host1"
        cls.regex1 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Connection error occurred on (.*)\. Host name: (.*)$"
        cls.regex2 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) (.*) (.*)$"

        cls.config = YamlConfig(parsers_path, rules_path, log_type_path)

    def test_is_free_parser_name(self):
        #These names aren't free because come from parsers.yaml file
        black_list = set()
        assert not self.config.is_free_parser_name('lostdata', black_list)
        assert not self.config.is_free_parser_name('connectionerror', black_list)
        assert not self.config.is_free_parser_name('datamigration', black_list)

    def _create_proposed_name_request(self, line, pattern, black_list):
        proposed_name = self.config.propose_parser_name(line, pattern, black_list)
        black_list.add(proposed_name)
        return proposed_name

    def test_simple_proposed_name(self):
        black_list = set()
        assert self._create_proposed_name_request(
            self.sample_line1, self.regex1, black_list
        ) == 'connection_error'
        assert self._create_proposed_name_request(
            self.sample_line1, self.regex1, black_list
        ) == 'connection_error1'
        assert self._create_proposed_name_request(
            self.sample_line1, self.regex1, black_list
        ) == 'connection_error2'

    def test_empty_building_words(self):
        black_list = set()
        assert self._create_proposed_name_request(
            self.sample_line2, self.regex2, black_list
        ) == 'parser_name1'
        assert self._create_proposed_name_request(
            self.sample_line2, self.regex2, black_list
        ) == 'parser_name2'
