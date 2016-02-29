from abc import ABCMeta, abstractmethod
import os

from whylog.config import YamlConfig


class AbstractClient(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_cause(self):
        pass


class WhylogClient(AbstractClient):
    """
	first naive client implementation
	"""

    def __init__(self, config):
        self.config = config

    def get_cause(self, offset, vim_line):
        pass

    def get_cause_tree(self, offset, vim_line):
        pass
