from abc import ABCMeta, abstractmethod, abstractproperty

import six


@six.add_metaclass(ABCMeta)
class AbstractAssistant(object):
    @abstractproperty
    def TYPE(self):
        """
        Assistant type. Must be unique for each assistant.
        """
        pass

    @abstractmethod
    def add_line(self, line_id, line_object):
        pass

    @abstractmethod
    def remove_line(self, line_id):
        pass

    @abstractmethod
    def get_pattern_match(self, line_id):
        pass

    @abstractmethod
    def update_by_pattern(self, line_id, pattern):
        pass

    @abstractmethod
    def update_by_guessed_pattern_match(self, line_id, pattern_id):
        pass

    @abstractmethod
    def guess_pattern_matches(self, line_id):
        pass

    @abstractmethod
    def set_converter(self, line_id, group_no, converter):
        pass

    @abstractmethod
    def validate(self, line_id):
        pass
