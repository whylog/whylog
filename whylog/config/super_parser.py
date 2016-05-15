import re
from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class AbstractSuperParser(object):
    @abstractmethod
    def get_ordered_group(self, line):
        pass


class RegexSuperParser(AbstractSuperParser):
    def __init__(self, regex_str, group_order, convertions):
        self.regex = re.compile(regex_str)
        self.group_order = group_order
        self.convertions = convertions

    def get_ordered_group(self, line):
        pass
