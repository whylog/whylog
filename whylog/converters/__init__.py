from abc import ABCMeta, abstractmethod

import dateutil.parser
import six
from frozendict import frozendict

from whylog.converters.exceptions import ConverterError


class ConverterType(object):
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

    @classmethod
    def safe_convert(cls, pattern_group):
        try:
            converted_val = cls.convert(pattern_group)
        except (ValueError, TypeError):
            raise ConverterError(pattern_group)
        else:
            return converted_val


class IntConverter(AbstractConverter):
    @classmethod
    def convert(cls, pattern_group):
        return int(pattern_group)


class FloatConverter(AbstractConverter):
    @classmethod
    def convert(cls, pattern_group):
        return float(pattern_group)


class StringConverter(AbstractConverter):
    @classmethod
    def convert(cls, pattern_group):
        return str(pattern_group)


#TODO: Simple date convertion will replace for concreate date format converter in the future
class DateConverter(AbstractConverter):
    @classmethod
    def convert(cls, pattern_group):
        return dateutil.parser.parse(pattern_group, fuzzy=True)

    @classmethod
    def safe_convert(cls, pattern_group):
        try:
            converted_val = cls.convert(pattern_group)
        except (ValueError, AttributeError):
            raise ConverterError(pattern_group)
        else:
            return converted_val


STRING = ConverterType.TO_STRING
CONVERTION_MAPPING = frozendict(
    {
        ConverterType.TO_STRING: StringConverter,
        ConverterType.TO_DATE: DateConverter,
        ConverterType.TO_INT: IntConverter,
        ConverterType.TO_FLOAT: FloatConverter
    }
)


def get_converter(converter_type):
    return CONVERTION_MAPPING[converter_type]
