from abc import ABCMeta

import six


@six.add_metaclass(ABCMeta)
class AbstractConstraint(object):
    pass


class TimeConstraint(AbstractConstraint):
    def __init__(self, groups=None, param_dict=None, params_checking=True):
        assert not params_checking
        pass

    @classmethod
    def verify(cls, param_dict, group_contents):
        # TODO remove mock
        return True


class IdenticalConstraint(AbstractConstraint):
    def __init__(self, groups=None, param_dict=None, params_checking=True):
        assert not params_checking

    @classmethod
    def verify(cls, param_dict, group_contents):
        if len(group_contents) <= 1:
            return False  # FIXME raise exception?
        return all(group_contents[0] == group for group in group_contents)


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
