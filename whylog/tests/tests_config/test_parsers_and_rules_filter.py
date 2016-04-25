import itertools
import os.path
from datetime import datetime
from unittest import TestCase

from whylog.config import YamlConfig
from whylog.front import FrontInput
from whylog.tests.utils import ConfigPathFactory

path_test_files = ['whylog', 'tests', 'tests_config', 'test_files']


class TestBasic(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection_error_line = "2016-04-12 23:54:45 Connection error occurred on comp1. Host name: host1"
        cls.lost_data_line = "2016-04-12 23:54:43 Data is missing at comp2. Loss = 230 GB. Host name: host2"
        cls.data_migration_line = "2016-04-12 23:54:40 Data migration from comp1 to comp2 failed. Host name: host2"

        path = os.path.join(*path_test_files)
        multiple_path = os.path.join(path, 'test_investigation_plan_files')
        parsers_path, rules_path, log_types_path = ConfigPathFactory.get_path_to_config_files(path)
        multiple_parsers_path, multiple_rules_path, _ = ConfigPathFactory.get_path_to_config_files(
            multiple_path
        )

        cls.simple_config = YamlConfig(parsers_path, rules_path, log_types_path)
        cls.multiple_parsers_config = YamlConfig(multiple_parsers_path, rules_path, log_types_path)
        cls.complexed_config = YamlConfig(
            multiple_parsers_path, multiple_rules_path, log_types_path
        )

    @classmethod
    def get_names_of_parsers(cls, parser_list):
        ordered = [parser.name for parser in parser_list]
        ordered.sort()
        return ordered

    def test_simple_parsers_filter(self):
        parsers, regex_params = self.simple_config._find_matching_parsers(
            self.lost_data_line, 'filesystem'
        )
        assert self.get_names_of_parsers(parsers) == ['lostdata']
        assert regex_params == {'lostdata': ('2016-04-12 23:54:43', 'comp2', '230', 'host2')}

        parsers, regex_params = self.simple_config._find_matching_parsers(
            self.lost_data_line, 'dummy'
        )
        assert self.get_names_of_parsers(parsers) == []
        assert regex_params == {}

        parsers, regex_params = self.simple_config._find_matching_parsers(
            self.connection_error_line, 'hydra'
        )
        assert self.get_names_of_parsers(parsers) == ['connectionerror']
        assert regex_params == {'connectionerror': ('2016-04-12 23:54:45', 'comp1', 'host1')}

    def test_multiple_parser_matching(self):
        parsers, regex_params = self.multiple_parsers_config._find_matching_parsers(
            self.lost_data_line, 'filesystem'
        )
        assert self.get_names_of_parsers(parsers) == ['lostdata', 'lostdatadate']
        assert regex_params == {
            'lostdata': ('2016-04-12 23:54:43', 'comp2', '230', 'host2'),
            'lostdatadate': ('2016-04-12 23:54:43',)
        }

    def test_simple_rule_filter(self):
        parsers, _ = self.simple_config._find_matching_parsers(self.lost_data_line, 'filesystem')
        rules = self.simple_config._filter_rule_set(parsers)
        assert len(rules) == 1
        assert rules[0]._effect.name == 'lostdata'
        assert self.get_names_of_parsers(rules[0]._causes) == ['connectionerror', 'datamigration']

    def test_empty_rule_filter(self):
        parsers, _ = self.simple_config._find_matching_parsers(self.connection_error_line, 'hydra')
        rules = self.simple_config._filter_rule_set(parsers)
        assert len(rules) == 0

    def test_multiple_rule_filter(self):
        parsers, _ = self.complexed_config._find_matching_parsers(self.lost_data_line, 'filesystem')
        rules = self.complexed_config._filter_rule_set(parsers)
        rules.sort(key=lambda x: x._effect.name)
        assert len(rules) == 2
        assert rules[0]._effect.name == 'lostdata'
        assert rules[1]._effect.name == 'lostdatadate'
        assert self.get_names_of_parsers(rules[0]._causes) == ['connectionerror', 'datamigration']
        assert self.get_names_of_parsers(rules[1]._causes) == ['connectionerror', 'datamigration']

    @classmethod
    def check_all_subparsers_have_same_log_type(cls, parser_list):
        log_types = [parser.log_type for parser in parser_list]
        distinct = list(set(log_types))
        assert len(distinct) == 1
        assert distinct == ['hydra']

    @classmethod
    def creating_concatenated_parsers_parametrized(cls, config):
        rule_chain = itertools.chain(*config._rules.values())
        concatenated_parsers = config._create_concatenated_parsers_for_investigation(rule_chain)
        assert len(concatenated_parsers) == 1
        parser_list = concatenated_parsers['hydra']._parsers
        cls.check_all_subparsers_have_same_log_type(parser_list)
        assert cls.get_names_of_parsers(parser_list) == ['connectionerror', 'datamigration']

    def test_creating_concatenated_parsers(self):
        self.creating_concatenated_parsers_parametrized(self.simple_config)
        self.creating_concatenated_parsers_parametrized(self.complexed_config)

    def test_creatig_effect_clues(self):
        #TODO: add some line source assert when FrontInput will contains LineSource or something like that
        offset = 42
        front_input = FrontInput(offset, self.lost_data_line, None)
        effect_params = {'lostdata': ("2015-12-03 12:11:00", "alfa21", "567.02", "101")}
        clues = self.simple_config._create_effect_clues(effect_params, front_input)
        assert len(clues) == 1
        clue = clues['lostdata']
        assert clue.regex_parameters == (datetime(2015, 12, 3, 12, 11), 'alfa21', '567.02', '101')
        assert clue.line_offset == offset
        assert clue.line_prefix_content == self.lost_data_line
