import os
from unittest import TestCase

import six

from whylog.assistant.pattern_match import ParamGroup
from whylog.assistant.regex_assistant import RegexAssistant
from whylog.assistant.regex_assistant.regex import create_obvious_regex
from whylog.config import YamlConfig
from whylog.config.investigation_plan import LineSource
from whylog.constraints import IdenticalConstraint
from whylog.converters import ConverterType
from whylog.front.utils import FrontInput
from whylog.teacher import Teacher
from whylog.teacher.user_intent import UserConstraintIntent, UserParserIntent
from whylog.tests.utils import ConfigPathFactory

path_test_files = ['whylog', 'tests', 'tests_teacher', 'test_files']


class TestRuleBase(TestCase):
    def setUp(self):
        """
        Creates teacher with sample Rule.
        """
        test_files_dir = 'empty_config_files'
        path = os.path.join(*path_test_files + [test_files_dir])
        parsers_path, rules_path, log_types_path = ConfigPathFactory.get_path_to_config_files(
            path, False
        )

        self.test_files = [parsers_path, rules_path, log_types_path]
        self._clean_test_files()

        yaml_config = YamlConfig(parsers_path, rules_path, log_types_path)
        regex_assistant = RegexAssistant()
        self.teacher = Teacher(yaml_config, regex_assistant)

        self.effect_id = 0
        self.effect_front_input = FrontInput(
            offset=42,
            line_content=r'2015-12-03 12:11:00 Error occurred in reading test',
            line_source=LineSource('sample_host', 'sample_path')
        )

        self.cause1_id = 1
        self.cause1_front_input = FrontInput(
            offset=30,
            line_content=r'2015-12-03 12:10:55 Data is missing on comp21',
            line_source=LineSource('sample_host1', 'sample_path1')
        )

        self.cause2_id = 2
        self.cause2_front_input = FrontInput(
            offset=21,
            line_content=r'2015-12-03 12:10:50 Data migration to comp21 failed in test 123',
            line_source=LineSource('sample_host2', 'sample_path2')
        )

        self.identical_groups = [(self.cause1_id, 2), (self.cause2_id, 2)]
        self.date_groups = [(self.effect_id, 1), (self.effect_id, 1)]

        self._add_rule()

    def _add_rule(self):
        self.teacher.add_line(self.effect_id, self.effect_front_input, effect=True)
        self.teacher.add_line(self.cause1_id, self.cause1_front_input)
        self.cause1_pattern = r'^([0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}) Data is missing on (.*)$'
        self.teacher.update_pattern(self.cause1_id, self.cause1_pattern)

        self.teacher.add_line(self.cause2_id, self.cause2_front_input)
        cause2_pattern = r'^([0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}) Data migration to (.*) failed in test (.*)$'
        self.teacher.update_pattern(self.cause2_id, cause2_pattern)

    def tearDown(self):
        self._clean_test_files()

    def _clean_test_files(self):
        for test_file in self.test_files:
            open(test_file, 'w').close()


class TestParser(TestRuleBase):
    def test_default_user_parser(self):
        user_rule = self.teacher.get_rule()
        effect_parser = user_rule.parsers[self.effect_id]
        wanted_effect_parser = UserParserIntent(
            'regex_assistant',
            'error_occurred_in_reading',
            r'([0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}) Error occurred in reading test$',
            None,
            [1],
            {
                1: ParamGroup(
                    content='2015-12-03 12:11:00',
                    converter_type=ConverterType.TO_DATE
                )
            },
            self.effect_front_input.line_content,
            self.effect_front_input.offset,
            self.effect_front_input.line_source,
            self.effect_id
        )  # yapf: disable
        assert wanted_effect_parser == effect_parser

    def test_setting_parser_name(self):
        effect_parser_name = self.teacher.get_rule().parsers[self.effect_id].pattern_name
        new_name = effect_parser_name + '_hello'
        self.teacher.set_pattern_name(self.effect_id, new_name)
        rule = self.teacher.get_rule()
        assert new_name == rule.parsers[self.effect_id].pattern_name

    def test_setting_converter(self):
        parser = self.teacher.get_rule().parsers[self.cause2_id]
        new_converter = ConverterType.TO_FLOAT
        assert not new_converter == parser.groups[3].converter_type

        self.teacher.set_converter(self.cause2_id, 3, new_converter)
        parser = self.teacher.get_rule().parsers[self.cause2_id]
        assert new_converter == parser.groups[3].converter_type

    def test_setting_primary_key(self):
        parser = self.teacher.get_rule().parsers[self.cause1_id]
        new_primary_key_groups = [1, 2]
        assert not new_primary_key_groups == parser.primary_key_groups
        self.teacher.set_primary_key(self.cause1_id, new_primary_key_groups)
        parser = self.teacher.get_rule().parsers[self.cause1_id]
        assert new_primary_key_groups == parser.primary_key_groups

    def test_setting_log_type(self):
        #TODO setting simple RegexSuperParser
        new_log_type = 'sample_log_type'
        self.teacher.set_log_type(self.effect_id, new_log_type)
        parser = self.teacher.get_rule().parsers[self.effect_id]
        assert new_log_type == parser.log_type_name

    def test_update_pattern(self):
        new_effect_pattern = r'^([0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}) Error occurred in (.*) test$'
        self.teacher.update_pattern(self.effect_id, new_effect_pattern)
        updated_pattern = self.teacher.get_rule().parsers[self.effect_id].pattern
        assert new_effect_pattern == updated_pattern

    def test_guess_patterns(self):
        effect_guessed_patterns = self.teacher.guess_patterns(self.effect_id)
        assert len(effect_guessed_patterns) > 1
        effect_guessed_regexes = [
            pattern_match.pattern for pattern_match in six.itervalues(effect_guessed_patterns)
        ]
        effect_obvious_regex = create_obvious_regex(self.effect_front_input.line_content)
        assert effect_obvious_regex in effect_guessed_regexes


class TestConstraints(TestRuleBase):
    def _register_identical_constraint(self, constraint_id=1):
        constraint = IdenticalConstraint(groups=self.identical_groups)
        self.teacher.register_constraint(constraint_id, constraint)

    def _constraints_absence_check(self):
        user_rule = self.teacher.get_rule()
        assert not user_rule.constraints
        assert not self.teacher._constraint_base
        assert not self.teacher._constraint_links.get_links()

    def _constraints_presence_check(self):
        user_rule = self.teacher.get_rule()
        assert user_rule.constraints
        assert self.teacher._constraint_base
        assert self.teacher._constraint_links.get_links()

    def test_register_and_remove_constraint(self):
        self._constraints_absence_check()

        constraint_id = 1
        constraint = IdenticalConstraint(groups=self.identical_groups)
        self.teacher.register_constraint(constraint_id, constraint)
        user_rule = self.teacher.get_rule()
        wanted_constraint = UserConstraintIntent(
            IdenticalConstraint.TYPE,
            self.identical_groups,
            constraint_id=constraint_id
        )
        assert wanted_constraint == user_rule.constraints[0]

        self._constraints_presence_check()

        self.teacher.remove_constraint(constraint_id)

        self._constraints_absence_check()

    def test_remove_line(self):
        """
        Removing line should indicate removal of related constraints.
        """
        self._register_identical_constraint()

        self._constraints_presence_check()

        self.teacher.remove_line(self.cause1_id)

        self._constraints_absence_check()

    def test_update_pattern(self):
        """
        Updating pattern of line should indicate removal of related constraints.
        (even if new pattern is the same as old or has the same groups)
        """
        self._register_identical_constraint()

        self._constraints_presence_check()

        self.teacher.update_pattern(self.cause1_id, self.cause1_pattern)

        self._constraints_absence_check()
