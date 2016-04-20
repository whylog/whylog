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
        cls.regex1 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Connection error occurred on (.*)\. Host name: (.*)$"

        cls.config = YamlConfig(parsers_path, rules_path, log_type_path)

    def test_is_free_parser_name(self):
        assert not self.config.is_free_parser_name('lostdata')
        assert not self.config.is_free_parser_name('connectionerror')
        assert not self.config.is_free_parser_name('datamigration')

    def test_simple_proposed_name(self):
        black_list = set()
        proposed_name = self.config.propose_parser_name(self.sample_line1, self.regex1, black_list)
        assert proposed_name == 'connection_error'

        black_list.add(proposed_name)
        proposed_name = self.config.propose_parser_name(self.sample_line1, self.regex1, black_list)
        assert proposed_name == 'error_occurred'

        black_list.add(proposed_name)
        proposed_name = self.config.propose_parser_name(self.sample_line1, self.regex1, black_list)
        assert proposed_name == 'occurred_on'

        black_list = black_list.union(set(['occurred_on', 'on_host', 'host_name']))
        proposed_name = self.config.propose_parser_name(self.sample_line1, self.regex1, black_list)
        assert proposed_name == 'connection_error1'
