import os.path
import itertools
from unittest import TestCase

from whylog.config import YamlConfig
from whylog.front import FrontInput

path_test_files = ['whylog', 'tests', 'tests_config', 'test_files', 'test_investigation_plan_files']


class TestBasic(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection_error_line = "2016-04-12 23:54:45 Connection error occurred on comp1. Host name: host1"
        cls.data_migration_line = "2016-04-12 23:54:40 Data migration from comp1 to comp2 failed. Host name: host2"
        cls.lost_data_line = "2016-04-12 23:54:43 Data is missing at comp2. Loss = 230 GB. Host name: host2"

        path = os.path.join(*path_test_files)
        cls.parsers_path = os.path.join(path, 'parsers.yaml')
        cls.multiple_parsers_path = os.path.join(path, 'multiple_match_parsers.yaml')
        cls.rules_path = os.path.join(path, 'rules.yaml')
        cls.log_type_path = os.path.join(path, 'log_types.yaml')
        cls.multiple_rules_path = os.path.join(path, 'multiple_rules.yaml')

    @classmethod
    def get_names_of_parsers(cls, parser_list):
        return sorted([parser.name for parser in parser_list])

    def test_simple_parsers_filter(self):
        config = YamlConfig(self.parsers_path, self.rules_path, self.log_type_path)
        front_input = FrontInput(None, self.lost_data_line, None)

        parsers, regex_params = config._find_matching_parsers(front_input, 'filesystem')
        assert TestBasic.get_names_of_parsers(parsers) == ['lostdata']
        assert regex_params == {'lostdata': ('2016-04-12 23:54:43', 'comp2', '230', 'host2')}

        parsers, regex_params = config._find_matching_parsers(front_input, 'dummy')
        assert TestBasic.get_names_of_parsers(parsers) == []
        assert regex_params == {}

        front_input = FrontInput(None, self.connection_error_line, None)
        parsers, regex_params = config._find_matching_parsers(front_input, 'hydra')
        assert TestBasic.get_names_of_parsers(parsers) == ['connectionerror']
        assert regex_params == {'connectionerror': ('2016-04-12 23:54:45', 'comp1', 'host1')}

    def test_multiple_parser_matching(self):
        config = YamlConfig(self.multiple_parsers_path, self.rules_path, self.log_type_path)
        front_input = FrontInput(None, self.lost_data_line, None)

        parsers, regex_params = config._find_matching_parsers(front_input, 'filesystem')
        assert TestBasic.get_names_of_parsers(parsers) == ['lostdata', 'lostdatadate']
        assert regex_params == {'lostdata': ('2016-04-12 23:54:43', 'comp2', '230', 'host2'),
                                'lostdatadate': ('2016-04-12 23:54:43',)}

    def test_simple_rule_filter(self):
        config = YamlConfig(self.parsers_path, self.rules_path, self.log_type_path)
        front_input = FrontInput(None, self.lost_data_line, None)

        parsers, _ = config._find_matching_parsers(front_input, 'filesystem')
        rules = config._filter_rule_set(parsers)
        assert len(rules) == 1
        assert rules[0]._effect.name == 'lostdata'
        assert TestBasic.get_names_of_parsers(rules[0]._causes) == ['connectionerror', 'datamigration']

    def test_empty_rule_filter(self):
        config = YamlConfig(self.parsers_path, self.rules_path, self.log_type_path)
        front_input = FrontInput(None, self.connection_error_line, None)

        parsers, _ = config._find_matching_parsers(front_input, 'hydra')
        rules = config._filter_rule_set(parsers)
        assert len(rules) == 0

    def test_multiple_rule_filter(self):
        config = YamlConfig(self.multiple_parsers_path, self.multiple_rules_path, self.log_type_path)
        front_input = FrontInput(None, self.lost_data_line, None)

        parsers, _ = config._find_matching_parsers(front_input, 'filesystem')
        rules = config._filter_rule_set(parsers)
        assert len(rules) == 2
        assert rules[0]._effect.name == 'lostdata'
        assert rules[1]._effect.name == 'lostdatadate'
        assert TestBasic.get_names_of_parsers(rules[0]._causes) == ['connectionerror', 'datamigration']
        assert TestBasic.get_names_of_parsers(rules[1]._causes) == ['connectionerror', 'datamigration']

    def test_creating_concatenated_parsers(self):
        config = YamlConfig(self.parsers_path, self.rules_path, self.log_type_path)
        rule_chain = itertools.chain(*config._rules.values())
        concatenated_parsers = config._create_concatenated_parser_for_investigation(rule_chain)
        assert len(concatenated_parsers) == 1
        parser_list = concatenated_parsers['hydra']._parsers
        assert TestBasic.get_names_of_parsers(parser_list) == ['connectionerror', 'datamigration']

