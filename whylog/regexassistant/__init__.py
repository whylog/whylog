class RegexAssistant(object):
    """
    Responsible for creating regex for each line of Rule.
    RegexAssistant helps user to write regex, it can also proposes regex.
    One RegexAssistant per one entering Rule.
    """

    def _obvious_regex(self, text):
        """
        Creates regex form text by simple transformation:
        - add backslash to special characters
        - text -> '^' + text + '$'
        :param text:
        :return:
        """
        # not finished yet
        return '^' + text + '$'

    def __init__(self, line_objects=tuple()):
        self.regexes = dict([(line, self._obvious_regex(line.line_content)) for line in line_objects
                            ])
        self.history = dict([(line, []) for line in line_objects])
        pass

    def add_lines(self, line_objects):
        for line in line_objects:
            self.regexes[line] = self._obvious_regex(line.line_content)
            self.history[line] = []

    def remove_lines(self, line_objects):
        for line in line_objects:
            del self.regexes[line]
            del self.history[line]

    def make_groups(self, intervals):
        """
        Improves regexes by adding to them regex groups corresponding to params in text.
        :param intervals: represents interval of text together with line_object
        """
        pass

    def remove_groups(self, intervals):
        """
        Removes regex groups from regexes.
        :param intervals: represents interval of text together with line_object
        """
        pass

    def verify_regex(self, line_object):
        """
        Check if created regex meets all requirements.
        For example, required is:
         - unambiguous matching line content
         - having a group with date
        It throws some exceptions if a requirement is not met
        :param line_object: line object, keeps specific information about line.
        """
        pass

    def load_regex(self, line_object, regex):
        """
        Loads regex proposed by user, verifies match, remember it in history.
        :param line_object: line object, keeps specific information about line.
        :param regex: proposed regex
        """
        pass

    def undo(self, line_object):
        """
        :return: next remembered regex (in reference to current place in history)
        """
        pass

    def redo(self, line_object):
        """
        :return: previous remembered regex (in reference to current place in history)
        """
        pass

    def guess_regex(self, line_object):
        """
        Guess regex. It includes guessing date format and regex groups.
        :param line_object: line object that keeps specific information about line.
        """
        pass

    def guess_groups(self, line_object):
        """
        Guess regex groups (params/variables )
        :return: regex improved by time format
        """
        pass

    def guess_time(self, line_object):
        """
        Guess time format
        :return: regex improved by time format
        """
        pass
