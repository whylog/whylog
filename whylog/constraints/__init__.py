from abc import ABCMeta

import six


@six.add_metaclass(ABCMeta)
class AbstractConstraint(object):
    pass


class TimeConstraint(AbstractConstraint):
    def __init__(self, params):
        pass

    @classmethod
    def verify(cls, param_dict, group_contents):
        return True


class IdenticalIntervals(AbstractConstraint):
    def __init__(self, params):
        pass

    @classmethod
    def verify(cls, param_dict, group_contents):
        if not group_contents:
            return False
        return all(group_contents[0] == group for group in group_contents)


class AnyValueIntervals(AbstractConstraint):
    def __init__(self, params):
        pass


class DifferentValueIntervals(AbstractConstraint):
    def __init__(self, params):
        pass


class ConstIntervals(AbstractConstraint):
    def __init__(self, params):
        pass


class ValueDeltaIntervals(AbstractConstraint):
    def __init__(self, params):
        """
        Sets Minimum and maximum difference between values of params (if values are numbers).
        """
        pass
