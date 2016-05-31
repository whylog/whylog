from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta

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
    MIN_VALUE = -2000000000
    MAX_VALUE = 2000000000

    @classmethod
    def switch_by_delta(cls, value, delta, delta_type=None):
        return value - delta

    @classmethod
    def convert(cls, pattern_group):
        return int(pattern_group)


class FloatConverter(AbstractConverter):
    MIN_VALUE = float('-inf')
    MAX_VALUE = float('inf')

    @classmethod
    def switch_by_delta(cls, value, delta, delta_type=None):
        return value - delta

    @classmethod
    def convert(cls, pattern_group):
        return float(pattern_group)


class StringConverter(AbstractConverter):
    @classmethod
    def convert(cls, pattern_group):
        return str(pattern_group)


#TODO: Simple date convertion will replace for concreate date format converter in the future
class DateConverter(AbstractConverter):
    MIN_VALUE = datetime.min
    MAX_VALUE = datetime.max

    @classmethod
    def switch_by_delta(cls, date, delta, delta_type):
        if not delta:
            if delta_type == "max":
                return cls.MIN_VALUE
            else:
                return date
        converted_delta = timedelta(seconds=delta)
        return date - converted_delta

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
