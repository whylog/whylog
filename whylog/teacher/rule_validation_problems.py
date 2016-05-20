import itertools
import six


class ValidationResult(object):
    def __init__(self, rule_problems, parser_problems, constraint_problems):
        """
        :param rule_problems: Problems related to whole rule
        :param parser_problems: Problems related to parsers, dict[parser id, problem]
        :param constraint_problems: Problems related to constraints, dict[constraint id, problem]
        :type rule_problems: list[RuleValidationProblem]
        :type parser_problems: dict[int, ParserValidationProblem]
        :type constraint_problems: dict[int, ConstraintValidationProblem]
        """
        self.rule_problems = rule_problems
        self.parser_problems = parser_problems
        self.constraint_problems = constraint_problems

    def is_acceptable(self):
        parser_problems_list = itertools.chain.from_iterable(six.itervalues(self.parser_problems))
        constraint_problems_list = itertools.chain.from_iterable(six.itervalues(self.constraint_problems))

        all_problems = itertools.chain.from_iterable(
            [self.rule_problems, parser_problems_list, constraint_problems_list]
        )
        return all([not problem.IS_FATAL for problem in all_problems])

    def in_parser_problems(self, parser_id, problem):
        problems = self.parser_problems.get(parser_id)
        if problems is None:
            return False
        return problem in problems

    def in_rule_problems(self, problem):
        return problem in self.rule_problems


class RuleValidationProblem(object):
    MESSAGE_TEMPLATE = 'Rule problem: %s'
    MESSAGE = ''
    IS_FATAL = True

    def __init__(self):
        pass

    def __eq__(self, other):
        return str(self) == str(other)

    def __str__(self):
        return self.MESSAGE_TEMPLATE % (self.MESSAGE,)


class ConstraintValidationProblem(RuleValidationProblem):
    MESSAGE_TEMPLATE = 'Constraint problem: %s'


class ParserValidationProblem(RuleValidationProblem):
    MESSAGE_TEMPLATE = 'Parser problem: %s'


class NoEffectParserProblem(RuleValidationProblem):
    MESSAGE = 'No effect parser'


class OneParserRuleProblem(RuleValidationProblem):
    MESSAGE = 'Rule should consist of more than one parser.'


class NotUniqueParserNameProblem(ParserValidationProblem):
    MESSAGE = 'Parser name is not unique.'


class NotSetLogTypeProblem(ParserValidationProblem):
    MESSAGE = 'Log type is not set.'


class InvalidPrimaryKeyProblem(ParserValidationProblem):
    MESSAGE = 'Primary key %s should be subset of pattern groups %s.'

    def __init__(self, primary_key, group_numbers):
        super(InvalidPrimaryKeyProblem, self).__init__()
        self.primary_key = primary_key
        self.group_numbers = group_numbers

    def __str__(self):
        return self.MESSAGE_TEMPLATE % (self.MESSAGE % (self.primary_key, self.group_numbers))
