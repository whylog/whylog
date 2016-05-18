import itertools

from collections import namedtuple

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
        errors = sorted(itertools.chain(*[result.errors for result in results]))
        warnings = sorted(itertools.chain(*[result.warnings for result in results]))
        return ValidationResult(errors, warnings)

    def acceptable(self):
        return not self.errors


class RuleValidationProblem(object):
    pass


class ConstraintValidationProblem(RuleValidationProblem):
    pass


class PatternAssistantValidationProblem(RuleValidationProblem):
    pass


class NotUniqueParserNameProblem(RuleValidationProblem):
    def __init__(self, line_id):
        self.line_id = line_id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return 'Parser name is not unique, line id: %s' % (self.line_id,)


class WrongLogTypeProblem(RuleValidationProblem):
    def __init__(self, line_id):
        self.line_id = line_id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return 'Log type is not set, line id: %s' % (self.line_id,)


class WrongPrimaryKeyProblem(RuleValidationProblem):
    def __init__(self, primary_key, group_numbers, line_id):
        self.primary_key = primary_key
        self.group_numbers = group_numbers
        self.line_id = line_id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return 'Primary key %s should be subset of pattern groups %s, line id: %s' % \
               (self.primary_key, self.group_numbers, self.line_id)
