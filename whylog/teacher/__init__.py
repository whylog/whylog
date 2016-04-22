import six

from whylog.teacher.constraint_links_base import ConstraintLinksBase
from whylog.teacher.mock_outputs import create_sample_rule
from whylog.teacher.user_intent import LineParamGroup


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
    """
    :type groups: list[LineParamGroup]
    """

    def __init__(self, line_object):
        self.line = line_object
        self.pattern_name = None
        self.log_type = None
        self.primary_keys = []


class Teacher(object):
    """
    Enable teaching new rule. One Teacher per one entering rule.

    :type pattern_assistant: AbstractAssistant
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

    def add_line(self, line_id, line_object, effect=False):
        """
        Adds new line to rule.

        If line_id already exists, old line is overwritten by new line
        and all constraints related to old line are removed.

        """
        if line_id in six.iterkeys(self._parsers):
            self.remove_line(line_id)
        if effect:
            self.effect_id = line_id
        self.pattern_assistant.add_line(line_id, line_object)
        self._parsers[line_id] = TeacherParser(line_object)
        #TODO: set default TeacherParser all fields

    def remove_line(self, line_id):
        """
        Removes line from rule.

        Assumption: line with line_id exists in rule.
        Removes also all constraints related to this line.
        """

        self._remove_constraints_by_line(line_id)
        self.pattern_assistant.remove_line(line_id)
        del self._parsers[line_id]

    def update_pattern(self, line_id, pattern):
        """
        Loads text pattern proposed by user, verifies if it matches line text.
        """
        #TODO update TeacherParser: pattern_name?, primary_key, groups
        self.pattern_assistant.update_by_pattern(line_id, pattern)

    def guess_pattern(self, line_id):
        """
        Returns list of guessed patterns for a line.
        """
        pattern_objects = self.pattern_assistant.guess_pattern_objects(line_id)
        return [pattern_object.pattern for pattern_object in pattern_objects]

    def choose_guessed_pattern(self, line_id, pattern_id):
        self.pattern_assistant.update_by_guessed_pattern_object(line_id, pattern_id)

    def set_pattern_name(self, line_id, name=None):
        if name:
            # TODO: ask config if such a name already exists
            # TODO: blacklist
            self._parsers[line_id].pattern_name = name
        else:
            # TODO: ask config for unique name
            self._parsers[line_id].pattern_name = "temporary_name"

    def set_converter(self, pattern_group, converter):
        self.pattern_assistant.set_converter(pattern_group.line_id, pattern_group.number, converter)

    def set_primary_key(self, line_id, group_numbers):
        self._parsers[line_id].primary_keys = group_numbers

    def set_log_type(self, line_id, log_type):
        self._parsers[line_id].log_type = log_type

    def register_constraint(self, constraint_id, pattern_groups, constraint):
        """
        Adds new constraint to rule.

        If constraint_id already exists, constraint with this constraint_id
        is overwritten by new constraint

        :param pattern_groups: groups in pattern that are linked by constraint
        :type pattern_groups: list[PatternGroup]
        """
        if constraint_id in six.iterkeys(self._constraint_base):
            self.remove_constraint(constraint_id)

        self._constraint_base[constraint_id] = constraint
        new_constraint_links = [
            (group.line_id, group.number, constraint_id) for group in pattern_groups
        ]
        self._constraint_links.add_links(new_constraint_links)

    def remove_constraint(self, constraint_id):
        """
        Removes constraint from rule.

        Assumption: Constraint already exists in rule.
        """
        self._constraint_links.remove_links_by_constraint(constraint_id)
        del self._constraint_base[constraint_id]

    def _remove_constraints_by_line(self, line_id):
        self._constraint_links.remove_links_by_line(line_id)
        self._sync_constraint_base_with_links()

    def _remove_constraint_by_group(self, group):
        self._constraint_links.remove_links_by_group(group.line_id, group.number)
        self._sync_constraint_base_with_links()

    def _sync_constraint_base_with_links(self):
        ids_from_links = self._constraint_links.distinct_constraint_ids()
        for constraint_id in six.iterkeys(self._constraint_base):
            if constraint_id not in ids_from_links:
                del self._constraint_base[constraint_id]

    def set_causes_relation(self, relation):
        """
        Determines which combinations of causes can cause effect.
        :param relation: kind of sentence made of AND, OR, brackets and cause symbols.
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
