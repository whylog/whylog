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


class NoTimeDeltasProblem(TimeConstraintProblem):
    TEMPLATE = 'Neither %s or %s were provided and at least one of them is mandatory'

    def __init__(self, min_delta_name, max_delta_name):
        super(NoTimeDeltasProblem, self).__init__()
        self.min_delta_name = min_delta_name
        self.max_delta_name = max_delta_name

    def __str__(self):
        return self.TEMPLATE % (self.min_delta_name, self.max_delta_name)


class MinGreaterThatMaxProblem(TimeConstraintProblem):
    TEMPLATE = 'Min time delta should equal or greater than max time delta'
