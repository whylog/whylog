from whylog.teacher.rule_validation_problems import ConstraintValidationProblem


class TimeConstraintProblem(ConstraintValidationProblem):
    pass


class MinGreaterThatMaxProblem(TimeConstraintProblem):
    TEMPLATE = 'Min time delta should equal or greater than max time delta'
