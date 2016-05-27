from whylog.teacher.rule_validation_problems import ConstraintValidationProblem


class TimeConstraintProblem(ConstraintValidationProblem):
    pass


class ParamConversionProblem(ConstraintValidationProblem):
    TEMPLATE = 'Cannot convert param value properly, param: %s, param value: %s, conversion: %s'

    def __init__(self, param_name, param_value, conversion):
        super(ParamConversionProblem, self).__init__()
        self.param_name = param_name
        self.param_value = param_value
        self.conversion = conversion

    def __str__(self):
        return self.TEMPLATE % (self.param_name, self.param_value, self.conversion)


class MinGreaterThatMaxProblem(TimeConstraintProblem):
    TEMPLATE = 'Min time delta should equal or greater than max time delta'
