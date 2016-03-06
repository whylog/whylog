from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class AbstractClient(object):
    @abstractmethod
    def get_cause(self, front_input):
        pass


class WhylogClient(AbstractClient):
    def __init__(self, config):
        self.config = config

    def get_cause(self, front_input):
        pass

    def get_cause_tree(self, front_input):
        pass
