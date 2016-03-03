from whylog.teacher.mockoutputs import create_sample_rule


class Interval(object):
    """
    Represents interval in line.
    """

    def __init__(self, start_offset, length, line):
        self.start_offset = start_offset
        self.length = length
        self.line = line


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

    def __init__(self, config, effect, causes=tuple()):
        self.config = config
        self._rule = Rule(effect)
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
        pass

    def set_causes_relation(self, relation):
        """
        Determines which combinations of causes can cause effect.
        :param relation: kind of sentence made of AND, OR, brackets and cause symbols.
        """
        pass

    def save(self):
        self.config.add_rule(create_sample_rule())
