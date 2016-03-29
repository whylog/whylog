from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class AbstractLogReader(object):
    @abstractmethod
    def get_causes(self, front_input):
        pass


class LogReader(AbstractLogReader):
    def __init__(self, config):
        self.config = config

    def get_causes(self, front_input):
        pass

    def get_causes_tree(self, front_input):
        pass
