from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta

import dateutil.parser
import six
from frozendict import frozendict

from whylog.config.exceptions import UnsupportedPrimaryKeyType
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


@six.add_metaclass(ABCMeta)
class DeltaConverter(AbstractConverter):
    MIN_DELTA_TYPE = 0
    MAX_DELTA_TYPE = 1

    @classmethod
    @abstractmethod
    def switch_by_delta(cls, value, delta, delta_type=None):
        pass


class IntConverter(DeltaConverter):
    MIN_VALUE = -six.MAXSIZE - 1
    MAX_VALUE = six.MAXSIZE

    @classmethod
    def switch_by_delta(cls, value, delta, delta_type=None):
        return value - delta

    @classmethod
    def convert(cls, pattern_group):
        return int(pattern_group)


class FloatConverter(DeltaConverter):
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


class DateConverter(DeltaConverter):
    MIN_VALUE = datetime.min
    MAX_VALUE = datetime.max

    @classmethod
    def switch_by_delta(cls, date, delta, delta_type=None):
        if not delta:
            if delta_type == cls.MAX_DELTA_TYPE:
                return cls.MIN_VALUE
            else:
                return date
        converted_delta = timedelta(seconds=delta)
        return date - converted_delta

    @classmethod
    def convert(cls, pattern_group):
        return dateutil.parser.parse(pattern_group)

    @classmethod
    def safe_convert(cls, pattern_group):
        try:
            converted_val = cls.convert(pattern_group)
        except (ValueError, AttributeError):
            raise ConverterError(pattern_group)
        else:
            return converted_val


@six.add_metaclass(ABCMeta)
class DeltaConverterFactory(object):
    @classmethod
    def get_converter(cls, converter_type):
        converter = DELTA_CONVERTION_MAPPING.get(converter_type)
        if converter is None:
            raise UnsupportedPrimaryKeyType(converter_type)
        return converter


STRING = ConverterType.TO_STRING
CONVERTION_MAPPING = frozendict(
    {
        ConverterType.TO_STRING: StringConverter,
        ConverterType.TO_DATE: DateConverter,
        ConverterType.TO_INT: IntConverter,
        ConverterType.TO_FLOAT: FloatConverter
    }
)

DELTA_CONVERTION_MAPPING = frozendict(
    {
        ConverterType.TO_DATE: DateConverter,
        ConverterType.TO_INT: IntConverter,
        ConverterType.TO_FLOAT: FloatConverter
    }
)


def get_converter(converter_type):
    return CONVERTION_MAPPING[converter_type]
