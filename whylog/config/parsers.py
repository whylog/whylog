import re
from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class AbstractParser(object):
    @abstractmethod
    def get_clue(self, line):
        pass


class RegexParser(AbstractParser):
    def __init__(self, name, regex, primary_key_groups, log_type, convertions):
        self.name = name
        self.regex_str = regex
        self.primary_key_groups = primary_key_groups
        self.log_type = log_type
        self.convertions = convertions

    def get_clue(self, line):
        pass

    def serialize(self):
        return {
            "name": self.name,
            "regex": self.regex_str,
            "primary_key_groups": self.primary_key_groups,
            "log_type": self.log_type,
            "convertions": self.convertions,
        }


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
        return RegexParser(
            parser_intent.regex_name, parser_intent.regex, parser_intent.primary_key_groups,
            parser_intent.log_type_name, parser_intent.data_conversions
        )

    @classmethod
    def from_dao(cls, serialized_parser):
        return RegexParser(**serialized_parser)


class ConcatedRegexParser(object):
    def __init__(self, parser_list):
        self._parsers = parser_list
        self._regex = re.compile(self._create_concated_regex())
        self._parsers_indexes = self._get_indexes_of_groups_for_parsers()

    def _create_concated_regex(self):
        return "|".join(["(" + parser.regex_str + ")" for parser in self._parsers])

    def _get_indexes_of_groups_for_parsers(self):
        indexes_dict = {}
        free_index = 0
        for parser in self._parsers:
            amount_of_group = parser.regex_str.count('(') - parser.regex_str.count('\(')
            indexes_dict[parser.name] = (free_index, amount_of_group)
            free_index += amount_of_group + 1
        return indexes_dict

    def get_extracted_regex_params(self, line):
        matched = self._regex.match(line)
        if matched is None:
            return {}
        clues = {}
        groups = matched.groups()
        for name, indexes in self._parsers_indexes.items():
            if groups[indexes[0]] is not None:
                clues[name] = [groups[i] for i in range(indexes[0] + 1, indexes[0] + indexes[1] + 1)]
        return clues
