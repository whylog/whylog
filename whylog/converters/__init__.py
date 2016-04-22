from abc import ABCMeta, abstractmethod

import dateutil.parser
import six
from frozendict import frozendict


@six.add_metaclass(ABCMeta)
class AbstractConverter(object):
    @classmethod
    @abstractmethod
    def convert(cls, pattern_group):
        pass


class IntConverter(AbstractConverter):
    @classmethod
    @abstractmethod
    def convert(cls, pattern_group):
        return int(pattern_group)


class FloatConverter(AbstractConverter):
    @classmethod
    @abstractmethod
    def convert(cls, pattern_group):
        return float(pattern_group)


# Simple date convertion will replace for concreate date format converter in the future
class DateConverter(AbstractConverter):
    @classmethod
    @abstractmethod
    def convert(cls, pattern_group):
        return dateutil.parser.parse(pattern_group, fuzzy=True)


STRING = 'string'
CONVERTION_MAPPING = frozendict(
    {
        'date': DateConverter,
        'int': IntConverter,
        'float': FloatConverter
    }
)
