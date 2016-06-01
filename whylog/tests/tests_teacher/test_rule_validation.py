from whylog.config.filename_matchers import WildCardFilenameMatcher
from whylog.config.log_type import LogType
from whylog.constraints import TimeConstraint
from whylog.converters import ConverterType
from whylog.tests.tests_teacher import TestRuleBase

from whylog.assistant.validation_problems import (  # isort:skip
    InvalidConverterProblem, InvalidPrimaryKeyProblem, NotMatchingPatternProblem
)
from whylog.teacher.rule_validation_problems import (  # isort:skip
    NoEffectParserProblem, NotSetLogTypeProblem, NotUniqueParserNameProblem, ParserCountProblem
)  # yapf: disable
from whylog.constraints.validation_problems import (  # isort:skip
    MinGreaterThatMaxProblem, NoTimeDeltasProblem, ParamConversionProblem
)


class TestValidationBase(TestRuleBase):
    def _check_if_parser_has_problem(self, parser_id, problem):
        validation_result = self.teacher.validate()
        problems = validation_result.parser_problems.get(parser_id)
        if problems is None:
            return False
        return problem in problems

    def _check_if_rule_has_problem(self, problem):
        validation_result = self.teacher.validate()
        return problem in validation_result.rule_problems

    def check_if_constraint_has_problem(self, constraint_id, problem):
        validation_result = self.teacher.validate()
        problems = validation_result.constraint_problems.get(constraint_id)
        if problems is None:
            return False
        return problem in problems

    def _initial_validation_check(self):
        validation_result = self.teacher.validate()
        assert not validation_result.is_acceptable()

        assert len(validation_result.parser_problems) == 3
        assert not validation_result.rule_problems
        assert not validation_result.constraint_problems

        assert self._check_if_parser_has_problem(self.effect_id, NotSetLogTypeProblem())
        assert self._check_if_parser_has_problem(self.cause1_id, NotSetLogTypeProblem())
        assert self._check_if_parser_has_problem(self.cause2_id, NotSetLogTypeProblem())


class TestRuleProblems(TestValidationBase):
    def test_no_effect_parser(self):
        self.teacher.remove_line(self.effect_id)
        assert self._check_if_rule_has_problem(NoEffectParserProblem())

        self.teacher.add_line(self.effect_id, self.effect_front_input, effect=True)
        assert not self._check_if_rule_has_problem(NoEffectParserProblem())

        self._initial_validation_check()

    def test_one_parser_rule(self):
        self.teacher.remove_line(self.cause1_id)
        self.teacher.remove_line(self.cause2_id)

        assert self._check_if_rule_has_problem(ParserCountProblem())

        self.teacher.add_line(self.cause1_id, self.cause1_front_input)
        self.teacher.add_line(self.cause2_id, self.cause2_front_input)

        assert not self._check_if_rule_has_problem(ParserCountProblem())

        self._initial_validation_check()


class TestParserProblems(TestValidationBase):
    def test_not_unique_parser_name(self):
        effect_parser_name = self.teacher.get_rule().parsers[self.effect_id].pattern_name

        self.teacher.set_pattern_name(self.cause1_id, effect_parser_name)

        assert self._check_if_parser_has_problem(self.effect_id, NotUniqueParserNameProblem())
        assert self._check_if_parser_has_problem(self.cause1_id, NotUniqueParserNameProblem())

        self.teacher.set_pattern_name(self.cause1_id, 'very_unlikely_name')

        assert not self._check_if_parser_has_problem(self.effect_id, NotUniqueParserNameProblem())
        assert not self._check_if_parser_has_problem(self.cause1_id, NotUniqueParserNameProblem())
        self._initial_validation_check()

    def test_not_set_log_type(self):
        assert self._check_if_parser_has_problem(self.effect_id, NotSetLogTypeProblem())

        sample_filename_matcher = WildCardFilenameMatcher(
            'localhost', 'sample_path', 'default', None
        )
        new_log_type = LogType('localhost', [sample_filename_matcher])
        self.teacher.set_log_type(self.effect_id, new_log_type)

        assert not self._check_if_parser_has_problem(self.effect_id, NotSetLogTypeProblem())

    def test_not_matching_pattern(self):
        not_matching_pattern = 'not matching pattern'
        self.teacher.update_pattern(self.effect_id, not_matching_pattern)
        assert self._check_if_parser_has_problem(self.effect_id, NotMatchingPatternProblem())

    def test_invalid_primary_key(self):
        unlikely_primary_key = [1500, 100, 900]
        self.teacher.set_primary_key(self.effect_id, unlikely_primary_key)
        parser_groups = self.teacher.get_rule().parsers[self.effect_id].groups.keys()
        assert self._check_if_parser_has_problem(
            self.effect_id, InvalidPrimaryKeyProblem(unlikely_primary_key, parser_groups)
        )

    def test_invalid_converter(self):
        date_group = 1
        self.teacher.set_converter(self.cause1_id, date_group, ConverterType.TO_FLOAT)
        group_content = self.teacher.get_rule().parsers[self.cause1_id].groups[date_group].content
        assert self._check_if_parser_has_problem(
            self.cause1_id, InvalidConverterProblem(group_content, ConverterType.TO_FLOAT)
        )
        machine_group = 2
        self.teacher.set_converter(self.cause1_id, machine_group, ConverterType.TO_DATE)
        group_content = self.teacher.get_rule().parsers[self.cause1_id].groups[
            machine_group].content
        assert self._check_if_parser_has_problem(
            self.cause1_id, InvalidConverterProblem(group_content, ConverterType.TO_DATE)
        )


class TestTimeConstraintProblems(TestValidationBase):
    def test_wrong_params_types(self):
        min_delta = 'foo'
        params = {TimeConstraint.MIN_DELTA: min_delta}
        time_constraint = TimeConstraint(self.date_groups, params)
        constraint_id = 1

        self.teacher.register_constraint(constraint_id, time_constraint)
        assert self.check_if_constraint_has_problem(
            constraint_id, ParamConversionProblem(
                TimeConstraint.MIN_DELTA, min_delta, TimeConstraint.PARAMS[TimeConstraint.MIN_DELTA]
            )
        )

    def test_min_greater_than_max(self):
        params = {TimeConstraint.MIN_DELTA: 2, TimeConstraint.MAX_DELTA: 1}
        time_constraint = TimeConstraint(self.date_groups, params)
        constraint_id = 1

        self.teacher.register_constraint(constraint_id, time_constraint)
        assert self.check_if_constraint_has_problem(constraint_id, MinGreaterThatMaxProblem())

        self.teacher.remove_constraint(constraint_id)
        assert not self.check_if_constraint_has_problem(constraint_id, MinGreaterThatMaxProblem())
        self._initial_validation_check()

    def test_no_deltas(self):
        params = {}
        time_constraint = TimeConstraint(self.date_groups, params)
        constraint_id = 1

        self.teacher.register_constraint(constraint_id, time_constraint)
        assert self.check_if_constraint_has_problem(
            constraint_id, NoTimeDeltasProblem(TimeConstraint.MIN_DELTA, TimeConstraint.MAX_DELTA)
        )

        self.teacher.remove_constraint(constraint_id)
        assert not self.check_if_constraint_has_problem(
            constraint_id, NoTimeDeltasProblem(TimeConstraint.MIN_DELTA, TimeConstraint.MAX_DELTA)
        )
        self._initial_validation_check()
