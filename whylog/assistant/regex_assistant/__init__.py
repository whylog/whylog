from whylog.assistant import AbstractAssistant
from whylog.assistant.regex_assistant.regex_object import RegexObject
from whylog.assistant.spans_finding import find_date_spans


class RegexAssistant(AbstractAssistant):
    """
    Responsible for creating regex for each line of Rule.
    RegexAssistant helps user to write regex, it can also propose regex.
    One RegexAssistant per one entering Rule.
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
        raise NotImplementedError

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
        """
        Guess regex. It includes guessing date and other regex groups.
        """

        regex_obj = self.regex_objects[line_id]

        date_spans = find_date_spans(regex_obj.line_text)

        group_spans = date_spans  #TODO: date_spans + other found spans

        regex_obj.update_forcefully(group_spans)
