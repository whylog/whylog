from unittest import TestCase

from whylog.teacher.rule_validation_problems import (
    ValidationResult, NotSetLogTypeProblem, NotUniqueParserNameProblem
)


class TestBasic(TestCase):
    def setUp(self):
        self.line1_id = 1
        line2_id = 2
        self.e1 = NotUniqueParserNameProblem(self.line1_id)
        e2 = NotSetLogTypeProblem(line2_id)
        w2 = NotUniqueParserNameProblem(line2_id)
        errors = [e2, self.e1]
        warnings = [w2]
        self.constraint_id = 3
        # TODO: create constraint problems with self.constraint_id
        self.validation_result = ValidationResult(errors, warnings)

    def test_select_parser_problems(self):
        self.validation_result.select_parser_problems(self.line1_id)
        filtered_problems = self.validation_result.select_parser_problems(self.line1_id)
        assert self.e1 in filtered_problems

    def test_select_constraint_problems(self):
        self.validation_result.select_parser_problems(self.constraint_id)
        filtered_problems = self.validation_result.select_constraint_problems(self.constraint_id)
        assert not filtered_problems
