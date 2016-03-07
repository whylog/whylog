from whylog.teacher.mock_outputs import create_sample_rule


class Interval(object):
    """
    Represents interval in line.
    """

    def __init__(self, start_offset, end_offset, line_id):
        self.start_offset = start_offset
        self.end_offset = end_offset
        self.line_id = line_id


class Teacher(object):
    """
    Enable teaching new rule. One Teacher per one entering rule.
    """

    def __init__(self, id_to_line_dict, effect_id, config):
        self.lines = dict(id_to_line_dict)
        self.effect_id = effect_id
        self.constraints = set()
        self.config = config

    def add_line(self, line_id, line_object):
        self.lines[line_id] = line_object

    def remove_line(self, line_id):
        del self.lines[id]
        if line_id == self.effect_id:
            # TODO: return something that represents warning "No effect line, remember to add it!"
            pass

    def update_regex(self, line_id, proposed_regex):
        """
        Loads regex proposed by user, verifies match.
        """
        pass

    def make_groups(self, intervals):
        """
        Improves regexes by adding to them regex groups corresponding to params in text.
        """
        pass

    def guess_regex(self, line_id):
        """
        Guess regex. It includes guessing date format and regex groups.
        """
        pass

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

    def _verify(self):
        """
        Verifies if regexes and constraints meet all requirements.
        E.g it is required regex match its line in one way only.
        """
        pass

    def save(self):
        """
        Verifies regexes and constraints. If they meet all requirements, saves Rule.
        """
        self.config.add_rule(create_sample_rule())
