class Interval(object):
    """
    Represents interval in line.
    """

    def __init__(self, start_offset, length, abstract_line):
        self.start_offset = start_offset
        self.length = length
        self.abstract_line = abstract_line


class Rule(object):
    """
    Represents rule entering by user.
    """

    def __init__(self, effect):
        self.effect = effect
        self.causes = set()
        self.constraints = set()


class Teacher(object):
    """
    Enable teaching new rule. One Teacher per one entering rule.
    """

    def __init__(self, effect, causes=None):
        self._rule = Rule(effect)
        if causes is not None:
            self._rule.causes.update(causes)

    def add_cause(self, cause):
        self._rule.causes.add(cause)

    def remove_cause(self, cause):
        self._rule.causes.remove(cause)

    def register_constraint(self, constraint):
        """
        Sample use:
        t = Teacher(effect, [cause1, cause2])
        t.register_constraint(TimeConstraint(effect, cause1, min_delta=-300, max_delta=1))
        t.register_constraint(IdenticalIntervals([interval1, interval2, interval3))
        """
        # in implementation remember to delete earlier added constraint
        # when the new one excludes the earlier.
        pass

    def set_causes_relation(self, relation):
        """
        Determines which combinations of causes can cause effect.
        :param relation: kind of sentence made of AND, OR, brackets and cause symbols.
        """
        pass

    def save(self):
        pass
