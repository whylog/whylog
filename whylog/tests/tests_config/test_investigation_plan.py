import os.path
from unittest import TestCase


from whylog.config import YamlConfig
from whylog.front import FrontInput

path_test_files = ['whylog', 'tests', 'tests_config', 'test_files']


class TestBasic(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection_error_line = "2016-04-12 23:54:45 Connection error occurred on comp1. Host name: host1"
        cls.data_migration_line = "2016-04-12 23:54:40 Data migration from comp1 to comp2 failed. Host name: host2"
        cls.lost_data_line = "2016-04-12 23:54:43 Data is missing at comp2. Loss = (.*) GB. Host name: host2"

        path = os.path.join(*path_test_files)
        parsers_path = os.path.join(path, 'parsers.yaml')
        rules_path = os.path.join(path, 'rules.yaml')
        log_type_path = os.path.join(path, 'log_types.yaml')

        cls.config = YamlConfig(parsers_path, rules_path, log_type_path)

    @classmethod
    def get_names_of_parsers(cls, parser_list):
        return [parser.name for parser in parser_list]

    def test_simple_parsers_filter(self):
        front_input = FrontInput(None, self.lost_data_line, None)
        parsers = self.config._find_matching_parsers(front_input, 'filesystem')
        assert TestBasic.get_names_of_parsers(parsers) == ['lost_data']
        parsers = self.config._find_matching_parsers(front_input, 'dummy')
        assert TestBasic.get_names_of_parsers(parsers) == []
