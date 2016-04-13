from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class AbstractAssistant(object):
    @abstractmethod
    def guess(self, guess_base):
        pass

    @abstractmethod
    def verify(self):
        pass
