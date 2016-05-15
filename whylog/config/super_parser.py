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

    def serialize(self):
        return {
                'regex_str': self.regex.pattern,
                'group_order': self.group_order,
                'convertions': self.convertions
                }

    def __eq__(self, other):
        return self.serialize() == other.serialize()

    def get_ordered_group(self, line):
        pass


@six.add_metaclass(ABCMeta)
class AbstractSuperParserFactory(object):
    @classmethod
    @abstractmethod
    def from_dao(cls, serialized):
        pass


class RegexSuperParserFactory(AbstractSuperParserFactory):
    @classmethod
    def from_dao(cls, serialized):
        return RegexSuperParser(**serialized)
