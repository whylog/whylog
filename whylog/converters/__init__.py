from abc import ABCMeta, abstractmethod

import dateutil.parser
import six
from frozendict import frozendict


class ConverterType:
    TO_DATE = 'date'
    TO_FLOAT = 'float'
    TO_INT = 'int'
    TO_STRING = 'string'


@six.add_metaclass(ABCMeta)
class AbstractConverter(object):
    @classmethod
    @abstractmethod
    def convert(cls, pattern_group):
        raise NotImplementedError


class IntConverter(AbstractConverter):
    @classmethod
    def convert(cls, pattern_group):
        return int(pattern_group)


class FloatConverter(AbstractConverter):
    @classmethod
    def convert(cls, pattern_group):
        return float(pattern_group)


#TODO: Simple date convertion will replace for concreate date format converter in the future
class DateConverter(AbstractConverter):
    @classmethod
    def convert(cls, pattern_group):
        return dateutil.parser.parse(pattern_group, fuzzy=True)


STRING = ConverterType.TO_STRING
CONVERTION_MAPPING = frozendict(
    {
        ConverterType.TO_DATE: DateConverter,
        ConverterType.TO_INT: IntConverter,
        ConverterType.TO_FLOAT: FloatConverter
    }
)
