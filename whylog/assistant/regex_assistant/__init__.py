from whylog.assistant import AbstractAssistant
from whylog.assistant.regex_assistant.regex import create_obvious_regex, regex_from_group_spans
from whylog.assistant.regex_assistant.regex_object import RegexObject


class RegexAssistant(AbstractAssistant):
    """
    Responsible for creating regex for each line of Rule.
    RegexAssistant helps user to write regex, it can also propose regex.
    One RegexAssistant per one entering Rule.

    :type regex_objects: dict[int, RegexObject]
    """

    def __init__(self):
        self.regex_objects = {}

    def add_line(self, line_id, line_object):
        regex_obj = RegexObject(line_object)
        self.regex_objects[line_id] = regex_obj

    def remove_line(self, line_id):
        del self.regex_objects[line_id]

    def update(self, line_id, regex):
        """
        Loads regex proposed by user, verifies match.
        """
        self.regex_objects[line_id].update_by_regex(regex)

    def verify(self, line_id):
        """
        Verifies regex properties such as:
        - matching a whole text
        - matching text in a one way only
        - proper data type assigned to regex group
        If properties are not met, proper exceptions are returned.
        """
        return self.regex_objects[line_id].verify()

    def make_groups(self, groups):
        """
        Improves regexes by adding to them regex groups corresponding to params in text.
        :param groups: pairs (line_id, group_id)
        """
        raise NotImplementedError

    def remove_groups(self, groups):
        """
        Improves regexes by removing regex groups corresponding to params in text.
        :param groups: pairs (line_id, group_id)
        """
        raise NotImplementedError

    def guess(self, line_id):
        regex_object = self.regex_objects[line_id]
        return regex_object.guessed_regex_objects
