import re
from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class AbstractParser(object):
    @abstractmethod
    def get_regex_params(self, line):
        pass


class RegexParser(AbstractParser):
    def __init__(self, name, regex, primary_key_groups, log_type, convertions):
        self.name = name
        self.regex_str = regex
        self.primary_key_groups = primary_key_groups
        self.log_type = log_type
        self.convertions = convertions

    def get_regex_params(self, line):
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
        forward, backward = self._create_concated_regexes()
        self._forward_regex = re.compile(forward)
        self._backward_regex = re.compile(backward)
        self._forward_parsers_indexes = self._get_indexes_of_groups_for_parsers(self._parsers)
        self._backward_parsers_indexes = self._get_indexes_of_groups_for_parsers(
            reversed(
                self._parsers
            )
        )
        self._numbers_in_list = self._number_in_list()

    def _create_concated_regexes(self):
        return (
            "|".join(
                "(" + parser.regex_str + ")" for parser in self._parsers
            ), "|".join(
                "(" + parser.regex_str + ")" for parser in reversed(self._parsers)
            )
        )

    def _get_indexes_of_groups_for_parsers(self, parser_list):
        indexes_dict = {}
        free_index = 0
        for parser in parser_list:
            amount_of_group = parser.regex_str.count('(') - parser.regex_str.count('\(')
            indexes_dict[parser.name] = (free_index, amount_of_group)
            free_index += amount_of_group + 1
        return indexes_dict

    def _number_in_list(self):
        regex_numbers = {}
        number = 0
        for parser in self._parsers:
            regex_numbers[parser.name] = number
            number += 1
        return regex_numbers

    def get_extracted_regex_params(self, line):
        forward_matched = self._forward_regex.match(line)
        backward_matched = self._backward_regex.match(line)
        if forward_matched is None:
            return {}
        clues = {}
        forward_groups = forward_matched.groups()
        backward_groups = backward_matched.groups()
        for name, indexes in self._forward_parsers_indexes.items():
            regex_index, regex_group_number = indexes[0], indexes[1]
            if forward_groups[regex_index] is not None:
                clues[name] = [
                    forward_groups[i]
                    for i in range(regex_index + 1, regex_index + regex_group_number + 1)
                ]
                if backward_groups[self._backward_parsers_indexes[name][0]] is None:
                    left = self._numbers_in_list[name] + 1
                    right = len(self._parsers) - 1
                    for parser in reversed(self._parsers):
                        if backward_groups[self._backward_parsers_indexes[parser.name][0]] is not None:
                            regex_index = self._backward_parsers_indexes[parser.name][0]
                            regex_group_number = self._backward_parsers_indexes[parser.name][1]
                            clues[parser.name] = [
                                backward_groups[i]
                                for i in range(regex_index + 1, regex_index + regex_group_number + 1)
                            ]
                            right -= 1
                            break
                        right -= 1
        return clues
