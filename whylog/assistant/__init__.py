from abc import ABCMeta, abstractmethod

import six

from whylog.assistant.const import AssistantType


@six.add_metaclass(ABCMeta)
class AbstractAssistant(object):
    @abstractmethod
    def guess(self, guess_base):
        pass

    @abstractmethod
    def verify(self):
        pass


class RegexAssistant(AbstractAssistant):
    """
    Responsible for creating regex for each line of Rule.
    RegexAssistant helps user to write regex, it can also propose regex.
    One RegexAssistant per one entering Rule.
    """

    def __init__(self):
        self.lines = {}
        self.regexes = {}
        self.assistant_type = AssistantType.REGEX

    def add_lines(self, id_to_line_dict):
        self.lines.update(id_to_line_dict)
        for line_id in id_to_line_dict:
            self.regexes[line_id] = self._obvious_regex(self.lines[line_id].line_content)

    def remove_lines(self, line_ids):
        for line_id in line_ids:
            del self.regexes[line_id]
            del self.lines[line_id]

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

    def update(self, line_id, regex):
        """
        Loads regex proposed by user, verifies match, remember it in history.
        :param line_object: line object, keeps specific information about line.
        :param regex: proposed regex
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

    def make_groups(self, intervals):
        """
        Improves regexes by adding to them regex groups corresponding to params in text.
        :param intervals: represents interval of text together with line_object
        """
        pass

    def guess(self, line_id):
        """
        Guess regex. It includes guessing date format and regex groups.
        :param line_object: line object that keeps specific information about line.
        """
        pass

    def _guess_groups(self, line_ids):
        """
        Guess regex groups (params/variables )
        :return: regex improved by time format
        """
        pass

    def _guess_time(self, line_id):
        """
        Guess time format
        :return: regex improved by time format
        """
        pass
