import os.path
from unittest import TestCase

import yaml

from whylog.config import YamlConfig
from whylog.config.parsers import RegexParserFactory
from whylog.config.rule import RegexRuleFactory
from whylog.teacher.user_intent import UserConstraintIntent, UserParserIntent, UserRuleIntent

# Constraint types
identical_constr = "identical"
different_constr = "different"
hetero_constr = "hetero"

# convertions
to_date = "date"

path_test_files = ['whylog', 'tests', 'tests_config', 'test_files']


class TestBasic(TestCase):
    def setUp(self):
        self.regex1 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Connection error occurred on (.*)\. Host name: (.*)$"
        self.regex2 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data migration from (.*) to (.*) failed\. Host name: (.*)$"
        self.regex3 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)\. Loss = (.*) GB\. Host name: (.*)$"

        self.parser_intent1 = UserParserIntent(
            "connectionerror", "hydra", self.regex1, [1], {1: to_date}
        )
        self.parser_intent2 = UserParserIntent(
            "datamigration", "hydra", self.regex2, [1], {1: to_date}
        )
        self.parser_intent3 = UserParserIntent(
            "lostdata", "filesystem", self.regex3, [1], {1: to_date}
        )

        parsers = {0: self.parser_intent1, 1: self.parser_intent2, 2: self.parser_intent3}
        effect_id = 2

        constraint1 = UserConstraintIntent(identical_constr, [[0, 2], [1, 2]])
        constraint2 = UserConstraintIntent(identical_constr, [[1, 3], [2, 2]])
        constraint3 = UserConstraintIntent(different_constr, [[1, 2], [1, 3]])
        constraint4 = UserConstraintIntent(
            hetero_constr, [[0, 3], [1, 4], [2, 4]], {
                "different": 1
            }
        )

        constraints = [constraint1, constraint2, constraint3, constraint4]

        self.user_intent = UserRuleIntent(effect_id, parsers, constraints)

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
        path = os.path.join(*path_test_files)
        parsers_path = os.path.join(path, 'parsers.yaml')
        rules_path = os.path.join(path, 'rules.yaml')
        log_type_path = os.path.join(path, 'log_type.yaml')

        config = YamlConfig(parsers_path, rules_path, log_type_path)
        assert len(config._rules) == 1
        rule = config._rules[0]
        assert sorted([cause.name for cause in rule._causes] + [rule._effect.name]) == sorted(
            parser.name for parser in config._parsers.values()
        )
