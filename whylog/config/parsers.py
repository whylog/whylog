from abc import ABCMeta, abstractmethod


class AbstractParser(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_clue(self, line):
        pass


class RegexParser(AbstractParser):
    def __init__(self, name, regex, log_type, params=None):
        self._name = name
        self._regex_str = regex
        self._params = params or []
        self._log_type = log_type

    def get_clue(self, line):
        pass
