import os
from unittest import TestCase

from whylog.assistant.pattern_match import ParamGroup
from whylog.assistant.regex_assistant import RegexAssistant
from whylog.config import YamlConfig
from whylog.config.investigation_plan import LineSource
from whylog.front.utils import FrontInput
from whylog.teacher import Teacher
from whylog.teacher.user_intent import UserParserIntent
from whylog.tests.utils import ConfigPathFactory

path_test_files = ['whylog', 'tests', 'tests_teacher', 'test_files']


class TestBase(TestCase):
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
        self._add_test_rule()

    def _add_test_rule(self):
        line_content = r'2015-12-03 12:11:00 Error occurred in reading test'
        line_source = LineSource('sample_host', 'sample_path')
        offset = 42
        self.effect_front_input = FrontInput(offset, line_content, line_source)
        self.effect_id = 0
        self.teacher.add_line(self.effect_id, self.effect_front_input, effect=True)

    def tearDown(self):
        self._clean_test_files()

    def _clean_test_files(self):
        for test_file in self.test_files:
            open(test_file, 'w').close()


class TestParser(TestBase):
    def test_default_user_parser(self):
        user_rule = self.teacher.get_rule()
        effect_parser = user_rule.parsers[self.effect_id]

        wanted_effect_parser = UserParserIntent(
            'regex_assistant',
            'error_occurred_in_reading',
            r'^([0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}) Error occurred in reading test$',
            None,
            [1],
            {
                1: ParamGroup(
                    content='2015-12-03 12:11:00',
                    converter='to_date'
                )
            },
            self.effect_front_input.line_content,
            self.effect_front_input.offset,
            self.effect_front_input.line_source,
        )
        assert wanted_effect_parser == effect_parser

