from abc import ABCMeta, abstractmethod


class AbstractClient(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_cause(self):
        pass


class WhylogClient(AbstractClient):
    def __init__(self, config):
        self.config = config

    def get_cause(self, offset, vim_line):
        pass

    def get_cause_tree(self, offset, vim_line):
        pass
