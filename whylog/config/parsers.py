from abc import ABCMeta, abstractmethod


class AbstractParser(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_clue(self, line):
        pass


class RegexParser(AbstractParser):
    def __init__(self, name, regex, params):
        pass

    def get_clue(self, line):
        pass
