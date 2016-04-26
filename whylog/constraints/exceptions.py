from whylog.exceptions import WhylogError


class VerificationError(WhylogError):
    pass


class UnsupportedConstraintTypeError(VerificationError):
    def __init__(self, constraint_data):
        self._constraint_data = constraint_data

    def __str__(self):
        return "No such constraint (%s) registered" % self._constraint_data['name']
