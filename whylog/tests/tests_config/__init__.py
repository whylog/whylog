import os.path
from unittest import TestCase

import yaml

from whylog.assistant.const import AssistantType
from whylog.config import YamlConfig
from whylog.config.parsers import RegexParserFactory
from whylog.config.rule import RegexRuleFactory
from whylog.teacher.user_intent import (
    LineParamGroup, UserConstraintIntent, UserParserIntent, UserRuleIntent
)

# Constraint types
identical_constr = "identical"
different_constr = "different"
hetero_constr = "hetero"

# convertions
to_date = "date"
to_string = "string"
to_int = "int"

path_test_files = ['whylog', 'tests', 'tests_config', 'test_files']


class TestBasic(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_line1 = "(2016-04-12 23:54:45) Connection error occurred on comp1. Host name: host1"
        cls.sample_line2 = "(2016-04-12 23:54:40) Data migration from comp1 to comp2 failed. Host name: host2"
        cls.sample_line3 = "(2016-04-12 23:54:43) Data is missing at comp2. Loss = (.*) GB. Host name: host2"

        cls.regex1 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Connection error occurred on (.*)\. Host name: (.*)$"
        cls.regex2 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data migration from (.*) to (.*) failed\. Host name: (.*)$"
        cls.regex3 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)\. Loss = (.*) GB\. Host name: (.*)$"

        regex_type = AssistantType.REGEX

        # yapf: disable
        cls.groups1 = {
            1: LineParamGroup("2016-04-12 23:54:45", to_date),
            2: LineParamGroup("comp1", to_string),
            3: LineParamGroup("host1", to_string)
        }
        cls.groups2 = {
            1: LineParamGroup("2016-04-12 23:54:40", to_date),
            2: LineParamGroup("comp2", to_string),
            3: LineParamGroup("host2", to_string)
        }
        cls.groups3 = {
            1: LineParamGroup("2016-04-12 23:54:43", to_date),
            2: LineParamGroup("comp2", to_string),
            3: LineParamGroup("150", to_int),
            4: LineParamGroup("host2", to_string)
        }

        cls.parser_intent1 = UserParserIntent(
            regex_type,
            "connectionerror",
            cls.regex1,
            "hydra",
            [1],
            cls.groups1,
            cls.sample_line1,
            line_offset=None,
            line_resource_location=None
        )
        cls.parser_intent2 = UserParserIntent(
            regex_type,
            "datamigration",
            cls.regex2,
            "hydra",
            [1],
            cls.groups2,
            cls.sample_line2,
            line_offset=None,
            line_resource_location=None
        )
        cls.parser_intent3 = UserParserIntent(
            regex_type,
            "lostdata",
            cls.regex3,
            "filesystem",
            [1],
            cls.groups3,
            cls.sample_line3,
            line_offset=None,
            line_resource_location=None
        )

        parsers = {0: cls.parser_intent1, 1: cls.parser_intent2, 2: cls.parser_intent3}
        effect_id = 2

        constraint1 = UserConstraintIntent(identical_constr, [[0, 2], [1, 2]])
        constraint2 = UserConstraintIntent(identical_constr, [[1, 3], [2, 2]])
        constraint3 = UserConstraintIntent(different_constr, [[1, 2], [1, 3]])
        constraint4 = UserConstraintIntent(
            hetero_constr, [[0, 3], [1, 4], [2, 4]], {
                "different": 1
            }
        )
        #  yapf: enable

        constraints = [constraint1, constraint2, constraint3, constraint4]

        cls.user_intent = UserRuleIntent(effect_id, parsers, constraints)

        path = os.path.join(*path_test_files)
        parsers_path = os.path.join(path, 'parsers.yaml')
        rules_path = os.path.join(path, 'rules.yaml')
        log_type_path = os.path.join(path, 'log_types.yaml')

        cls.config = YamlConfig(parsers_path, rules_path, log_type_path)

    def test_simple_transform(self):
        rule = RegexRuleFactory.create_from_intent(self.user_intent)

        assert rule._effect.regex_str == self.regex3
        assert sorted(cause.regex_str for cause in rule._causes) == [self.regex1, self.regex2]

    def test_parser_serialization(self):
        parser1 = RegexParserFactory.create_from_intent(self.parser_intent1)
        parser2 = RegexParserFactory.create_from_intent(self.parser_intent2)
        parser3 = RegexParserFactory.create_from_intent(self.parser_intent3)
        parsers_list = [parser1, parser2, parser3]

        parsers_dao_list = [parser.serialize() for parser in parsers_list]
        dumped_parsers = yaml.dump_all(parsers_dao_list, explicit_start=True)
        loaded_parsers = [
            RegexParserFactory.from_dao(dumped_parser)
            for dumped_parser in yaml.load_all(dumped_parsers)
        ]
        dumped_parsers_again = yaml.dump_all(
            [parser.serialize() for parser in loaded_parsers],
            explicit_start=True
        )

        assert dumped_parsers_again == dumped_parsers

    def test_loading_single_rule_its_parsers(self):
        assert len(self.config._rules) == 1
        rule = self.config._rules[0]
        assert sorted([cause.name for cause in rule._causes] + [rule._effect.name]) == sorted(
            parser.name for parser in self.config._parsers.values()
        )

    def test_loading_log_types(self):
        assert len(self.config._log_types) == 2
        assert sorted(self.config._log_types.keys()) == ['apache', 'default']
        assert len(self.config._log_types['default']._filename_matchers) == 2
        assert len(self.config._log_types['apache']._filename_matchers) == 1
