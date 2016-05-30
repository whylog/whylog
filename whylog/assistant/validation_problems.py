from whylog.teacher.rule_validation_problems import ParserValidationProblem


class NotMatchingPatternProblem(ParserValidationProblem):
    TEMPLATE = 'Pattern does not match line'


class InvalidConverterProblem(ParserValidationProblem):
    TEMPLATE = 'Wrong group converter, converter type: %s, group: %s'

    def __init__(self, group, converter):
        super(InvalidConverterProblem, self).__init__()
        self.group = group
        self.converter = converter

    def __str__(self):
        return self.TEMPLATE % (self.converter, self.group)


class InvalidPrimaryKeyProblem(ParserValidationProblem):
    TEMPLATE = 'Primary key %s should be subset of pattern groups %s.'

    def __init__(self, primary_key, group_numbers):
        super(InvalidPrimaryKeyProblem, self).__init__()
        self.primary_key = primary_key
        self.group_numbers = group_numbers

    def __str__(self):
        return self.TEMPLATE % (self.primary_key, self.group_numbers)
