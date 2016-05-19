import itertools
from abc import ABCMeta, abstractmethod
from collections import namedtuple

import six


ValidationResult = namedtuple('ValidationResult', ['errors', 'warnings'])


class ValidationResult(object):
    def __init__(self, errors, warnings):
        """
        :param errors: problems preventing form rule saving
        :param warnings: problems accepted while rule saving
        :type errors: [RuleValidationProblem]
        :type warnings: [RuleValidationProblem]
        """
        self.errors = errors
        self.warnings = warnings

    @classmethod
    def result_from_results(cls, results):
        errors = sum([result.errors for result in results], [])
        warnings = sum([result.warnings for result in results], [])
        return ValidationResult(errors, warnings)

    def acceptable(self):
        return not self.errors

    def select_parser_problems(self, line_id):
        return [
            problem for problem in itertools.chain(self.warnings, self.errors)
            if problem.concerns_parser(line_id)
        ]  # yapf: disable

    def select_constraint_problems(self, constraint_id):
        return [
            problem for problem in itertools.chain(self.warnings, self.errors)
            if problem.concerns_constraint(constraint_id)
        ]  # yapf: disable


@six.add_metaclass(ABCMeta)
class RuleValidationProblem(object):
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @abstractmethod
    def concerns_parser(self, parser_id):
        pass

    @abstractmethod
    def concerns_constraint(self, constraint_id):
        pass


class ConstraintValidationProblem(RuleValidationProblem):
    def __init__(self, constraint_id):
        self.constraint_id = constraint_id

    def get_constraint_id(self):
        return self.constraint_id

    def concerns_parser(self, parser_id):
        return False

    def concerns_constraint(self, constraint_id):
        return self.constraint_id == constraint_id


class ParserValidationProblem(RuleValidationProblem):
    def __init__(self, line_id):
        self.line_id = line_id

    def get_line_id(self):
        return self.line_id

    def concerns_parser(self, parser_id):
        return self.line_id == parser_id

    def concerns_constraint(self, constraint_id):
        return False


class NotUniqueParserNameProblem(ParserValidationProblem):
    def __str__(self):
        return 'Parser name is not unique, line id: %s' % (self.line_id,)


class NotSetLogTypeProblem(ParserValidationProblem):
    def __str__(self):
        return 'Log type is not set, line id: %s' % (self.line_id,)


class InvalidPrimaryKeyProblem(ParserValidationProblem):
    def __init__(self, line_id, primary_key, group_numbers):
        super(InvalidPrimaryKeyProblem, self).__init__(line_id)
        self.primary_key = primary_key
        self.group_numbers = group_numbers

    def __str__(self):
        return 'Primary key %s should be subset of pattern groups %s, line id: %s' % \
               (self.primary_key, self.group_numbers, self.line_id)
