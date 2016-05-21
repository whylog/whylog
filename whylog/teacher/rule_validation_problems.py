import itertools
from abc import ABCMeta, abstractproperty

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
        constraint_problems_list = itertools.chain.from_iterable(
            six.itervalues(self.constraint_problems)
        )  # yapf: disable

        all_problems = itertools.chain.from_iterable(
            (self.rule_problems, parser_problems_list, constraint_problems_list)
        )
        return all(not problem.IS_FATAL for problem in all_problems)


@six.add_metaclass(ABCMeta)
class RuleValidationProblem(object):
    @abstractproperty
    def TEMPLATE(self):
        """
        Text that explains problem
        """
        pass

    IS_FATAL = True

    def __init__(self):
        pass

    def __eq__(self, other):
        return str(self) == str(other)

    def __str__(self):
        return self.TEMPLATE


class ConstraintValidationProblem(RuleValidationProblem):
    pass


class ParserValidationProblem(RuleValidationProblem):
    pass


class NoEffectParserProblem(RuleValidationProblem):
    TEMPLATE = 'No effect parser'


class ParserCountProblem(RuleValidationProblem):
    TEMPLATE = 'Rule should consist of at least 2 parsers.'


class NotUniqueParserNameProblem(ParserValidationProblem):
    TEMPLATE = 'Parser name is not unique.'


class NotSetLogTypeProblem(ParserValidationProblem):
    TEMPLATE = 'Log type is not set.'


class InvalidPrimaryKeyProblem(ParserValidationProblem):
    TEMPLATE = 'Primary key %s should be subset of pattern groups %s.'

    def __init__(self, primary_key, group_numbers):
        super(InvalidPrimaryKeyProblem, self).__init__()
        self.primary_key = primary_key
        self.group_numbers = group_numbers

    def __str__(self):
        return self.TEMPLATE % (self.primary_key, self.group_numbers)
