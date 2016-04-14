from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class AbstractConstraint(object):
    @abstractmethod
    def save(self, rulebase_rule):
        pass


class TimeConstraint(AbstractConstraint):
    def __init__(self, line_earlier, line_later, min_delta=None, max_delta=None):
        pass

    @classmethod
    def verify(cls, clues, min_delta, max_delta):
        # TODO here the constraint verification should take place and bool should be returned
        pass


class IdenticalIntervals(AbstractConstraint):
    def __init__(self, intervals):
        pass


class AnyValueIntervals(AbstractConstraint):
    def __init__(self, intervals):
        pass


class DifferentValueIntervals(AbstractConstraint):
    def __init__(self, intervals):
        pass


class ConstIntervals(AbstractConstraint):
    def __init__(self, intervals):
        pass


class ValueDeltaIntervals(AbstractConstraint):
    def __init__(self, interval_lower, interval_greater, min_delta=None, max_delta=None):
        """
        Sets Minimum and maximum difference between values of params (if values are numbers).
        """
        pass
