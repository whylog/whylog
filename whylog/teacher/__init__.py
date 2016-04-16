from whylog.teacher.constraint_links_base import ConstraintLinksBase
from whylog.teacher.mock_outputs import create_sample_rule


class PatternGroup(object):
    """
    Keeps "coordinates" of group that represents param in text

    :param line_id: id of line to which group belongs.
    :param number: number of group in line.
                   Groups don't overlap. Numeration from left, from 1.
    """

    def __init__(self, line_id, group_number_in_line):
        self.line_id = line_id
        self.number = group_number_in_line


class TeacherParser(object):
    def __init__(self, line_object):
        self.line = line_object
        self.pattern_name = None
        self.log_type = None
        self.primary_keys = []


class Teacher(object):
    """
    Enable teaching new rule. One Teacher per one entering rule.

    :type _parsers: dict[int, TeacherParser]
    :type _constraint_base: dict[int, AbstractConstraint]
    :param _constraint_links: Keeps links between constraints and groups.
                              Link between constraint C and group G exists
                              if C describes relation between G and other groups.
    :type _constraint_links: ConstraintLinksBase
    """

    def __init__(self, config, pattern_assistant):
        self.config = config
        self.pattern_assistant = pattern_assistant

        self._parsers = {}
        self._constraint_base = {}
        self._constraint_links = ConstraintLinksBase()
        self.effect_id = None
        self.pair = None

    def add_line(self, line_id, line_object, effect=False):
        """
        Adds new line to rule.

        If line_id already exists, old line is overwritten by new line
        and all constraints related to old line are removed.

        """

        if line_id in self._parsers.keys():
            self.remove_line(line_id)
        if effect:
            self.effect_id = line_id
        self.pattern_assistant.add_line(line_id, line_object)
        self._parsers[line_id] = TeacherParser(line_object)

    def remove_line(self, line_id):
        """
        Removes line from rule.

        Assumption: line with line_id exists in rule.
        Removes also all constraints related to this line.
        """

        self._remove_constraints_by_line(line_id)
        self.pattern_assistant.remove(line_id)
        del self._parsers[line_id]

    def update_pattern(self, line_id, proposed_pattern):
        """
        Loads text pattern proposed by user, verifies if it matches line text.
        """
        pass

    def make_group(self, line_id, span):
        """
        Improves text pattern by adding group corresponding to param in text.

        Removes (or maybe updates) constraints related to groups in line with line_id
        """
        pass

    def remove_group(self, pattern_group):
        """
        Improves text pattern by removing group corresponding to param in text.

        Removes (or maybe updates) constraints related to groups in line with line_id
        """
        pass

    def guess_pattern(self, line_id):
        """
        Guess text pattern for line text.
        """
        pass

    def set_pattern_name(self, line_id, name):
        pass

    def set_converter(self, pattern_group, converter):
        pass

    def set_primary_key(self, line_id, group_numbers):
        pass

    def set_log_type(self, line_id, log_type):
        pass

    def register_constraint(self, constr_id, pattern_groups, constraint):
        """
        Adds new constraint to rule.

        If constr_id already exists, constraint with this constr_id
        is overwritten by new constraint

        :param pattern_groups: groups in pattern that are linked by constraint
        :type pattern_groups: list[PatternGroup]
        """
        if constr_id in self._constraint_base.keys():
            self.remove_constraint(constr_id)

        self._constraint_base[constr_id] = constraint
        new_constraint_links = [
            (group.line_id, group.number, constr_id) for group in pattern_groups
        ]
        self._constraint_links.add_links(new_constraint_links)

    def remove_constraint(self, removing_constr_id):
        """
        Removes constraint from rule.

        Assumption: Constraint already exists in rule.
        """
        self._constraint_links.remove_links_where(constr_id=removing_constr_id)
        del self._constraint_base[removing_constr_id]

    def _remove_constraints_by_line(self, line_id):
        self._constraint_links.remove_links_where(line_id=line_id)
        self._sync_constraint_base_with_links()

    def _remove_constraint_by_group(self, group):
        self._constraint_links.remove_links_where(line_id=group.line_id, group_no=group.number)
        self._sync_constraint_base_with_links()

    def _sync_constraint_base_with_links(self):
        ids_from_links = self._constraint_links.distinct_constraint_ids()
        for constr_id in self._constraint_base.keys():
            if constr_id not in ids_from_links:
                del self._constraint_base[constr_id]

    def set_causes_relation(self, relation):
        """
        Determines which combinations of causes can cause effect.
        :param relation: kind of sentence made of AND, OR, brackets and cause symbols.
        """
        pass

    def _verify(self):
        """
        Verifies if text patterns and constraints meet all requirements.
        E.g it is required text pattern match its line in one way only.
        """
        pass

    def test_rule(self):
        """
        Simulates searching causes with alreday created rule.
        """
        pass

    def get_rule(self):
        """
        Creates rule for Front that will be shown to user
        """
        #TODO: remove mock
        return create_sample_rule()

    def save(self):
        """
        Verifies text patterns and constraints. If they meet all requirements, saves Rule.
        """
        #TODO: remove mock
        self.config.add_rule(create_sample_rule())
