from abc import ABCMeta, abstractmethod

import regex
import six
from frozendict import frozendict


@six.add_metaclass(ABCMeta)
class AbstractParser(object):
    @abstractmethod
    def get_regex_params(self, line):
        pass


class RegexParser(AbstractParser):
    def __init__(self, name, regex_str, primary_key_groups, log_type, convertions):
        self.name = name
        self.regex_str = regex_str
        self.regex = regex.compile(self.regex_str)
        self.primary_key_groups = primary_key_groups
        self.log_type = log_type
        self.convertions = convertions

    def get_regex_params(self, line):
        matches = self.regex.match(line)
        if matches is not None:
            return list(matches.groups())

    def serialize(self):
        return {
            "name": self.name,
            "regex_str": self.regex_str,
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
    NO_MATCH = frozendict()

    def __init__(self, parser_list):
        self._parsers = parser_list
        forward, backward = self._create_concated_regexes()
        self._forward_regex = regex.compile(forward)
        self._backward_regex = regex.compile(backward)
        self._forward_parsers_indexes = self._get_indexes_of_groups_for_parsers(self._parsers)
        self._backward_parsers_indexes = self._get_indexes_of_groups_for_parsers(
            reversed(
                self._parsers
            )
        )
        self._numbers_in_list = self._number_in_list()
        self._forward_group_index_to_regex = self._create_group_index_to_regex_name(
            self._forward_parsers_indexes
        )
        self._backward_group_index_to_regex = self._create_group_index_to_regex_name(
            self._backward_parsers_indexes
        )

    def _create_concated_regexes(self):
        forward_regex = "|".join("(" + parser.regex_str + ")" for parser in self._parsers)
        backward_regex = "|".join(
            "(" + parser.regex_str + ")" for parser in reversed(self._parsers)
        )
        return forward_regex, backward_regex

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

    def _create_group_index_to_regex_name(self, parsers_indexes):
        index_to_regex = {}
        for name, indexes in parsers_indexes.items():
            index_to_regex[indexes[0]] = name
        return index_to_regex

    def get_extracted_regex_params(self, line):
        forward_matched = self._forward_regex.match(line)
        if forward_matched is None:
            return ConcatedRegexParser.NO_MATCH
        forward_groups = forward_matched.groups()
        if self._is_matched_last_group(forward_groups):
            return self._extract_params_from_last_regex(forward_groups)
        backward_groups = self._backward_regex.match(line).groups()
        forward_matched_regex_name, only_one = self._check_that_only_one_regex_matched(
            forward_groups, backward_groups
        )
        regex_params = self._extract_regex_params_by_regex_name(
            forward_groups, forward_matched_regex_name, self._forward_parsers_indexes
        )
        clues = {forward_matched_regex_name: regex_params}
        if only_one:
            return clues
        backward_matched_regex_name = self._get_first_matches_regex_name(
            backward_groups, self._backward_group_index_to_regex
        )
        regex_params = self._extract_regex_params_by_regex_name(
            backward_groups, backward_matched_regex_name, self._backward_parsers_indexes
        )
        clues[backward_matched_regex_name] = regex_params
        left = self._numbers_in_list[forward_matched_regex_name] + 1
        right = self._numbers_in_list[backward_matched_regex_name] - 1
        self._brute_subregexes_matching(clues, left, right, line)
        return clues

    def _extract_regex_params_by_regex_name(self, groups, matched_regex_name, parsers_indexes):
        start_index = parsers_indexes[matched_regex_name][0]
        number_of_groups = parsers_indexes[matched_regex_name][1]
        regex_params = self._extract_regex_params(groups, number_of_groups, start_index)
        return regex_params

    def _get_first_matches_regex_name(self, groups, group_index_to_regex):
        for group in groups:
            if group is not None:
                first_matched = groups.index(group)
                break
        return group_index_to_regex[first_matched]

    def _check_that_only_one_regex_matched(self, forward_groups, backward_groups):
        regex_name = self._get_first_matches_regex_name(
            forward_groups, self._forward_group_index_to_regex
        )
        return regex_name, backward_groups[
            self._backward_parsers_indexes[regex_name][
                0
            ]
        ] is not None

    def _extract_params_from_last_regex(self, forward_groups):
        last_regex_name = self._parsers[len(self._parsers) - 1].name
        last_regex_params = self._extract_regex_params_by_regex_name(
            forward_groups, last_regex_name, self._forward_parsers_indexes
        )
        return {last_regex_name: last_regex_params}

    def _is_matched_last_group(self, groups):
        return groups[len(groups) - 1] is not None

    def _extract_regex_params(self, groups, regex_group_number, regex_index):
        return [
            groups[i]
            for i in six.moves.range(regex_index + 1, regex_index + regex_group_number + 1)
        ]

    def _brute_subregexes_matching(self, clues, left, right, line):
        for i in six.moves.range(left, right + 1):
            match = self._parsers[i].get_regex_params(line)
            if match is not None:
                clues[self._parsers[i].name] = match
