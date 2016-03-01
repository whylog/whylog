from abc import ABCMeta, abstractmethod


class AbstractParser(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_clue(self, line):
        pass


class RegexParser(AbstractParser):
    def __init__(self, name, regex, params, log_type):
        pass

    def get_clue(self, line):
        pass


class WildCardParser(AbstractParser):
    def __init__(self, name):
        pass

    def get_clue(self, line):
        pass
