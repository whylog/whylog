import abc


class AbstractAssistant(object):
    @abc.abstractmethod
    def guess(self, guess_base):
        pass

    @abc.abstractmethod
    def verify(self):
        pass

    @abc.abstractmethod
    def undo(self, history_keeper):
        pass

    @abc.abstractmethod
    def redo(self, history_keeper):
        pass


class RegexAssistant(AbstractAssistant):
    """
    Responsible for creating regex for each line of Rule.
    RegexAssistant helps user to write regex, it can also propose regex.
    One RegexAssistant per one entering Rule.
    """

    def __init__(self, effect, line_objects=tuple()):
        self.regexes = {}
        self.add_lines([effect])
        self.add_lines(line_objects)
        # TODO: line indexing (here and in other methods)
        # after adding new line, we assign an index for it
        # and modify this line using line index.

    def add_lines(self, line_objects):
        for line in line_objects:
            self.regexes[line] = self._obvious_regex(line.line_content)

    def remove_lines(self, line_objects):
        for line in line_objects:
            del self.regexes[line]

    def _obvious_regex(self, text):
        """
        Creates regex form text by simple transformation:
        - backslash before special character
        - text -> '^' + text + '$'
        :param text:
        :return:
        """
        # not finished yet
        return '^' + text + '$'

    def make_groups(self, intervals):
        """
        Improves regexes by adding to them regex groups corresponding to params in text.
        :param intervals: represents interval of text together with line_object
        """
        pass

    def verify(self):
        """
        Check if created regexes meet all requirements.
        For example, required is:
         - regex should match its line in one way only.
        It throws some exceptions if a requirement is not met
        """
        pass

    def update_regex(self, line_object, regex):
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

    def guess(self, line_object):
        """
        Guess regex. It includes guessing date format and regex groups.
        :param line_object: line object that keeps specific information about line.
        """
        pass

    def _guess_groups(self, line_object):
        """
        Guess regex groups (params/variables )
        :return: regex improved by time format
        """
        pass

    def _guess_time(self, line_object):
        """
        Guess time format
        :return: regex improved by time format
        """
        pass
