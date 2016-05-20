import itertools

#ValidationResult = namedtuple('ValidationResult', ['parser_problems', 'rule_problems'])


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


class RuleValidationProblem(object):
    MESSAGE_TEMPLATE = 'Rule problem: %s'
    MESSAGE = ''

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return self.MESSAGE_TEMPLATE % (self.MESSAGE,)


class ConstraintValidationProblem(RuleValidationProblem):
    MESSAGE_TEMPLATE = 'Constraint problem: %s'


class ParserValidationProblem(RuleValidationProblem):
    MESSAGE_TEMPLATE = 'Parser problem: %s'


class NotUniqueParserNameProblem(ParserValidationProblem):
    MESSAGE = 'Parser name is not unique.'


class NotSetLogTypeProblem(ParserValidationProblem):
    MESSAGE = 'Log type is not set.'


class InvalidPrimaryKeyProblem(ParserValidationProblem):
    MESSAGE = 'Primary key %s should be subset of pattern groups %s.'

    def __init__(self, primary_key, group_numbers):
        self.primary_key = primary_key
        self.group_numbers = group_numbers

    def __str__(self):
        return self.MESSAGE_TEMPLATE % (self.MESSAGE % (self.primary_key, self.group_numbers))
