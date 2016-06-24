from abc import ABCMeta, abstractmethod

import six

from whylog.config.utils import regex
from whylog.converters import CONVERTION_MAPPING, STRING
from whylog.converters.exceptions import UnsupportedConverterError


@six.add_metaclass(ABCMeta)
class AbstractParser(object):
    @abstractmethod
    def get_regex_params(self, line):
        pass


class RegexParser(AbstractParser):
    """
    Represents regular expression used for searching some data in log file.
    RegexParser has an unique name. Some groups of regex can be signed as primary.
    It means that log file which has line matched with this regex is order by values
    of this group. Every regex belongs for single log type. Convertions in regex has a
    knowledge about casting regex groups content. At last line content is a sample line
    which matches with regex. It's used to show how concrete regex works. For example
    which segments of line are catch by its groups.
    """

    def __init__(self, name, line_content, regex_str, primary_key_groups, log_type, convertions):
        self.name = name
        self.line_content = line_content
        self.regex_str = regex_str
        self.regex = regex.compile(self.regex_str)
        self.primary_key_groups = primary_key_groups
        self.log_type = log_type
        self.convertions = convertions

    def get_regex_params(self, line):
        matches = self.regex.match(line)
        if matches is not None:
            return matches.groups()

    def serialize(self):
        return {
            "name": self.name,
            "regex_str": self.regex_str,
            "primary_key_groups": self.primary_key_groups,
            "log_type": self.log_type,
            "convertions": self.convertions,
            "line_content": self.line_content
        }

    def convert_params(self, params):
        """
        Converts single parser tuple groups to tuple with converted elems
        Sample convertion:
            params: ('2015-12-03 12:10:10', '2100', 'postgres_db')
            return: (datetime(2015, 12, 3, 12, 10, 10), 2100, 'postgres_db')
        """
        converted_params = []
        for i in six.moves.range(len(params)):
            group_type = self.convertions.get(i + 1, STRING)
            if group_type == STRING:
                converted_params.append(params[i])
                continue
            converter = CONVERTION_MAPPING.get(group_type)
            if converter is None:
                raise UnsupportedConverterError(group_type)
            converted_params.append(converter.convert(params[i]))
        return tuple(converted_params)

    def get_primary_key_group(self):
        assert len(self.primary_key_groups) <= 1
        if not self.primary_key_groups:
            return None, None
        primary_key_group = self.primary_key_groups[0]
        return primary_key_group, self.convertions.get(primary_key_group, 'string')

    def is_primary_key(self, group_number):
        assert len(self.primary_key_groups) <= 1
        return group_number == self.primary_key_groups[0]

    def __repr__(self):
        return "(RegexParser: %s, %s, %s, %s, %s, %s)" % (
            self.name, self.regex_str, self.line_content, self.convertions, self.log_type,
            self.primary_key_groups
        )


@six.add_metaclass(ABCMeta)
class AbstractParserFactory(object):
    @classmethod
    @abstractmethod
    def create_from_intent(cls, parser_intent):
        pass

    @classmethod
    @abstractmethod
    def from_dao(cls, serialized_parser):
        pass


class RegexParserFactory(object):
    @classmethod
    def create_from_intent(cls, parser_intent):
        convertions = dict(
            (group_id, group.converter_type)
            for group_id, group in six.iteritems(parser_intent.groups)
        )
        return RegexParser(
            parser_intent.pattern_name, parser_intent.line_content, parser_intent.pattern,
            parser_intent.primary_key_groups, parser_intent.log_type_name, convertions
        )

    @classmethod
    def from_dao(cls, serialized_parser):
        return RegexParser(**serialized_parser)
