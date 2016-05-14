from whylog.exceptions import WhylogError


class ConstraintError(WhylogError):
    pass


class VerificationError(ConstraintError):
    pass


class UnsupportedConstraintTypeError(VerificationError):
    def __init__(self, constraint_data):
        self._constraint_data = constraint_data

    def __str__(self):
        return "No such constraint (%s) registered" % self._constraint_data['name']


class WrongConstraintClassSetup(VerificationError):
    def __init__(self, constraint_type):
        self._constraint_type = constraint_type

    def __str__(self):
        return "Constraint object '%s' was incorrectly constructed" % self._constraint_type


class ConstructorParamsError(ConstraintError):
    def __init__(self, constraint_type, correct_param_names, incorrect_param_names):
        self.constraint_type = constraint_type
        self.correct_params_names = correct_param_names
        self.incorrect_params_names = incorrect_param_names

    def __str__(self):
        return 'Wrong params names in constraint constructor: %s, actual names: %s, should be: %s' % (
            self.constraint_type, self.incorrect_params_names, self.correct_params_names
        )


class ConstructorGroupsCountError(ConstraintError):
    def __init__(self, constraint_type, groups_count, minimal_groups_count, maximal_groups_count):
        self.constraint_type = constraint_type
        self.groups_count = groups_count
        self.minimal_groups_count = minimal_groups_count
        self.maximal_groups_count = maximal_groups_count

    def __str__(self):
        return 'Wrong groups count in constraint: %s, has %s groups, should be at least: %s, at most %s' % (
            self.constraint_type, self.groups_count, self.minimal_groups_count,
            self.maximal_groups_count
        )
