from abc import ABCMeta, abstractmethod

import six

NOT_IMPLEMENTED_ERROR_MESSAGE = "Subclass should implement this"


@six.add_metaclass(ABCMeta)
class AbstractAssistant(object):
    @abstractmethod
    def add_line(self, line_id, line_object):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR_MESSAGE)

    @abstractmethod
    def remove_line(self, line_id):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR_MESSAGE)

    @abstractmethod
    def get_pattern_object(self, line_id):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR_MESSAGE)

    @abstractmethod
    def update_by_pattern(self, line_id, pattern):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR_MESSAGE)

    @abstractmethod
    def update_by_guessed_pattern_object(self, line_id, pattern_id):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR_MESSAGE)

    @abstractmethod
    def guess_pattern_objects(self, line_id):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR_MESSAGE)

    @abstractmethod
    def set_converter(self, line_id, group_no, converter):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR_MESSAGE)

    @abstractmethod
    def verify(self):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR_MESSAGE)
