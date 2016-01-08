class Interval(object):
    """
    Represents interval in line.
    """

    def __init__(self, start_offset, length, abstract_line):
        self._start_offset = start_offset
        self._length = length
        self._abstract_line = abstract_line

    def get_start_offset(self):
        return self._start_offset

    def get_length(self):
        return self._length

    def get_location(self):
        return self._abstract_line


class Rule(object):
    """
    Represents rule entering by user.
    """

    def __index__(self, effect):
        self._effect = effect
        self._causes = set()

    def add_cause(self, cause):
        self._causes.add()

    def remove_cause(self, cause):
        self.causes.remove(cause)


class Teacher(object):
    """
    Enable teaching new rule. One Teacher per one entering rule.
    """

    def __init__(self, effect, causes=None):
        self._rule = Rule(effect)
        for cause in causes:
            self._rule.add_cause(cause)

    def add_cause(self, cause):
        self._rule.add_cause(cause)

    def remove_cause(self, cause):
        self._rule.remove_cause(cause)

    def set_equals(self, interval_list):
        pass

    def set_different(self, interval_list):
        pass

    def set_const(self, interval_list):
        pass

    def set_params_dependencies(self, interval1, interval2, val):
        pass

    def set_time_dependencies(self, abstract_line1, abstract_line2, time):
        pass

    def set_causes_relation(self, relation):
        pass

    def undo(self):
        pass

    def redo(self):
        pass

    def save(self):
        pass
