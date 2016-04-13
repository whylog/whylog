from whylog.teacher.mock_outputs import create_sample_rule
from whylog.teacher.user_intent import UserRuleIntent


class Teacher(object):
    """
    Enable teaching new rule. One Teacher per one entering rule.
    """

    def __init__(self, config, pattern_assistant):
        self.config = config
        self.pattern_assistant = pattern_assistant
        self._lines = {}  # line_id to line_object dict
        self._constraints = {}  # constraint_id to constraint dict

    def add_line(self, line_id, line_object, effect=False):
        pass

    def remove_line(self, line_id):
        pass

    def update_pattern(self, line_id, proposed_pattern):
        """
        Loads text pattern proposed by user, verifies if it matches line text.
        """
        pass

    def make_group(self, line_id, span):
        """
        Improves text pattern by adding group corresponding to param in text.
        """
        pass

    def remove_group(self, line_id, group_id):
        """
        Improves text pattern by removing group corresponding to param in text.
        """
        pass

    def guess_pattern(self, line_id):
        """
        Guess text pattern for line text.
        """
        pass

    def set_pattern_name(self, line_id, name):
        pass

    def set_converter(self, line_id, group, converter):
        pass

    def set_primary_key(self, line_id, groups):
        pass

    def set_log_type(self, line_id, log_type):
        pass

    def register_constraint(self, constr_id, constr_type, groups, params=None):
        pass

    def remove_constraint(self, constr_id):
        pass

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

    def get_rule(self):
        """
        Creates rule for Front, that will be shown to user
        """
        return create_sample_rule()
        pass

    def test_rule(self):
        """
        Simulates searching causes with alreday created rule.
        """
        pass

    def save(self):
        """
        Verifies text patterns and constraints. If they meet all requirements, saves Rule.
        """
        self.config.add_rule(create_sample_rule())
