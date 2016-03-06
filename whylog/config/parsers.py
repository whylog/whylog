from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class AbstractParser(object):
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
