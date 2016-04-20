from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class AbstractAssistant(object):
    @abstractmethod
    def add_line(self, line_id, line_object):
        pass

    @abstractmethod
    def remove_line(self, line_id):
        pass

    @abstractmethod
    def guess(self, guess_base):
        pass

    @abstractmethod
    def verify(self):
        pass
