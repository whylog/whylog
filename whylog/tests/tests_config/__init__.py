import os.path
from unittest import TestCase
import yaml

from whylog.config import YamlConfig
from whylog.config.rule import RegexRuleFactory
from whylog.config.parsers import RegexParserFactory
from whylog.teacher.user_intent import UserConstraintIntent, UserParserIntent, UserRuleIntent

# Constraint types
identical_constr = "identical"
different_constr = "different"
hetero_constr = "hetero"

# convertions
to_date = "date"

regex1 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Connection error occurred on (.*)\. Host name: (.*)$"
regex2 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data migration from (.*) to (.*) failed\. Host name: (.*)$"
regex3 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)\. Loss = (.*) GB\. Host name: (.*)$"

parser_intent1 = UserParserIntent("hydra", regex1, [1], {1: to_date})
parser_intent2 = UserParserIntent("hydra", regex2, [1], {1: to_date})
parser_intent3 = UserParserIntent("filesystem", regex3, [1], {1: to_date})

path_test_files = ['whylog', 'tests', 'tests_config', 'test_files']


class TestBasic(TestCase):
    """
    content1 = "2015-12-03 12:08:09 Connection error occurred on alfa36. Host name: 2"
    content2 = "2015-12-03 12:10:10 Data migration from alfa36 to alfa21 failed. Host name: 2"
    content3 = "2015-12-03 12:11:00 Data is missing at alfa21. Loss = 567.02 GB. Host name: 101"
    """

    def test_simple_transform(self):
        parsers = {0: parser_intent1, 1: parser_intent2, 2: parser_intent3}
        effect_id = 2

        constraint1 = UserConstraintIntent(identical_constr, [(0, 2), (1, 2)])
        constraint2 = UserConstraintIntent(identical_constr, [(1, 3), (2, 2)])
        constraint3 = UserConstraintIntent(different_constr, [(1, 2), (1, 3)])
        constraint4 = UserConstraintIntent(
            hetero_constr, [
                (0, 3), (1, 4), (2, 4)
            ], {"different": 1}
        )
        constraints = [constraint1, constraint2, constraint3, constraint4]

        user_intent = UserRuleIntent(effect_id, parsers, constraints)
        rule = RegexRuleFactory.create_from_intent(user_intent)

        assert rule._effect.regex_str == regex3
        assert sorted(cause.regex_str for cause in rule._causes) == [regex1, regex2]

        path = os.path.join(*path_test_files)
        parsers_path = os.path.join(path, 'parsers.yaml')
        rules_path = os.path.join(path, 'rules.yaml')

        config = YamlConfig(parsers_path, rules_path, None)
        config.add_rule(user_intent)

    def test_parser_serialization(self):
        parser1 = RegexParserFactory.create_from_intent(parser_intent1)
        parser2 = RegexParserFactory.create_from_intent(parser_intent2)
        parser3 = RegexParserFactory.create_from_intent(parser_intent3)
        parsers_list = [parser1, parser2, parser3]

        parsers_dao_list = [parser.to_data_access_object_form() for parser in parsers_list]
        dumped_parsers = yaml.dump_all(parsers_dao_list, explicit_start=True)
        loaded_parsers = [
            dumped_parser.create_parser() for dumped_parser in yaml.load_all(dumped_parsers)
        ]
        dumped_parsers_again = yaml.dump_all(
            [parser.to_data_access_object_form() for parser in loaded_parsers],
            explicit_start=True
        )

        assert dumped_parsers_again == dumped_parsers

    def test_save_regex_file(self):
        path = os.path.join(*path_test_files)
        parsers_path = os.path.join(path, 'parsers.yaml')
        rules_path = os.path.join(path, 'rules.yaml')

        config = YamlConfig(parsers_path, rules_path, None)
        print config._rules
