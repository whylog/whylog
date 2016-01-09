class Constraint(object):
    def __init__(self):
        pass


class TimeConstraint(Constraint):
    def __init__(self, abstract_line_earlier, abstract_line_later, min_delta=None, max_delta=None):
        pass


class IdenticalIntervals(Constraint):
    def __init__(self, interval_list):
        pass


class AnyValueIntervals(Constraint):
    def __init__(self, interval_list):
        pass


class DifferentValueIntervals(Constraint):
    def __init__(self, interval_list):
        pass


class ConstIntervals(Constraint):
    def __init__(self, Interval_list):
        pass


class ValueDeltaIntervals(Constraint):
    def __init__(self, interval_lower, interval_greater, min_delta=None, max_delta=None):
        """
        Sets Minimum and maximum difference between values of params (if values are numbers).
        """
        pass
