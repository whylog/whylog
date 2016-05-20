from whylog.config.filename_matchers import WildCardFilenameMatcher
from whylog.config.log_type import LogType
from whylog.teacher.rule_validation_problems import (
    OneParserRuleProblem, NoEffectParserProblem, NotSetLogTypeProblem, NotUniqueParserNameProblem,
)
from whylog.tests.tests_teacher import TestBase


class TestValidationBase(TestBase):
    def _initial_validation_check(self):
        validation_result = self.teacher.validate()
        assert not validation_result.is_acceptable()

        assert len(validation_result.rule_problems) == 1
        assert len(validation_result.parser_problems) == 1
        assert not validation_result.constraint_problems

        assert validation_result.in_parser_problems(self.effect_id, NotSetLogTypeProblem())
        assert validation_result.in_rule_problems(OneParserRuleProblem())


class TestRuleValidationTest(TestValidationBase):
    def test_no_effect_parser(self):
        self.teacher.remove_line(self.effect_id)

        validation_result = self.teacher.validate()
        assert validation_result.in_rule_problems(NoEffectParserProblem())

        self.teacher.add_line(self.effect_id, self.effect_front_input, effect=True)

        validation_result = self.teacher.validate()
        assert not validation_result.in_rule_problems(NoEffectParserProblem())
        self._initial_validation_check()

    def test_one_parser_rule(self):
        validation_result = self.teacher.validate()
        assert validation_result.in_rule_problems(OneParserRuleProblem())

        self.teacher.add_line(self.cause1_id, self.cause1_front_input)

        validation_result = self.teacher.validate()
        assert not validation_result.in_rule_problems(OneParserRuleProblem())

        self.teacher.remove_line(self.cause1_id)
        self._initial_validation_check()


class TestParserValidationTest(TestValidationBase):
    def test_not_unique_parser_name(self):
        effect_parser_name = self.teacher.get_rule().parsers[self.effect_id].pattern_name

        self.teacher.add_line(self.cause1_id, self.cause1_front_input)
        self.teacher.set_pattern_name(self.cause1_id, effect_parser_name)

        validation_result = self.teacher.validate()
        assert validation_result.in_parser_problems(self.effect_id, NotUniqueParserNameProblem())
        assert validation_result.in_parser_problems(self.cause1_id, NotUniqueParserNameProblem())

        self.teacher.remove_line(self.cause1_id)

        validation_result = self.teacher.validate()
        assert not validation_result.in_parser_problems(self.effect_id, NotUniqueParserNameProblem())
        assert not validation_result.in_parser_problems(self.cause1_id, NotUniqueParserNameProblem())
        self._initial_validation_check()

    def test_not_set_log_type(self):
        validation_result = self.teacher.validate()
        assert validation_result.in_parser_problems(self.effect_id, NotSetLogTypeProblem())

        sample_filename_matcher = WildCardFilenameMatcher(
            'localhost', 'sample_path', 'default', None
        )
        new_log_type = LogType('localhost', [sample_filename_matcher])
        self.teacher.set_log_type(self.effect_id, new_log_type)

        validation_result = self.teacher.validate()
        assert not validation_result.in_parser_problems(self.effect_id, NotSetLogTypeProblem())



