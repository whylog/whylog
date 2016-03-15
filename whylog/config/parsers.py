from abc import ABCMeta, abstractmethod

import six
from frozendict import frozendict

IMPORTED_RE = False

try:
    import regex
except ImportError:
    import re as regex
    IMPORTED_RE = True
"""
This handling of import regex error does not really means that
we are able to work without regex being installed. It means that
whylog can work with these python versions, which don't handle
regex module(like pypy, pypy3). So if you use cpython 2.5-3.5
please install regex module. That will improve whylog performance.
"""


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
            return matches.groups()

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


class ConcatenatedRegexParser(object):
    NO_MATCH = frozendict()

    def __init__(self, parser_list):
        self._parsers = parser_list
        if IMPORTED_RE:
            return
        forward, backward = self._create_concatenated_regexes()
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

    def _create_concatenated_regexes(self):
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
        """
        Extracted groups from subregexes that matched with line
        :param line: line from parsed file
        :returns: dict of regexname to tuple of extracted regex params which match with line
        line = "2015-12-03 12:11:00 Data is missing at alfa21. Loss = 567.02 GB. Host name: 101"
        Example of returned data: {
            "lost_data": ("2015-12-03 12:11:00", "alfa21", "567.02", "101"),
            "lost_data_date": ("2015-12-03 12:11:00",),
            "lost_data_suffix": ("2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"),
        }
        Sample forward concatenated regex : (a)|(b)|(c)|(d)|(e)
        Sample backward concatenated regex: (e)|(d)|(c)|(b)|(a)
        where a, b, c, d, e are subregexes. Subregexes can have own groups
        We need to backward concatenated regex because '|' operator isn't greed
        Flow:
            1. Handle case when regex module is not installed by matching many regexes
            2. Check if forward concatenated regex matched anything, if not return NO_MATCH
            3. Now we know that some subregexes matches to line.
                In majority of cases only one regex matches.
            4. Find which subregex matched. Extract groups from it.
            5. If it was last subregex return value from 4th point. It's true that only one subregex matches
            6. Now we must use backward concatenated regex to check if only one subregex matched.
                if yes return values from 4th point.
            7. Now we know more than one subregex matched. Check which subregex was matched by backward regex.
                Extract groups from it.
            8. Now we must check if other subregexes matched with line. We only have to check the ones that
                are beetween subregex found in 4th and 7th points. For example:
                 In 4th we found subregex a. In 7th we found e. Now we must check if b, c, d are matching to line
            9. Return merged data from 4th, 7th and 8th points.
        """
        if IMPORTED_RE:
            extracted_regex_params = {}
            self._brute_subregexes_matching(extracted_regex_params, 0, len(self._parsers) - 1, line)
            return extracted_regex_params
        forward_matched = self._forward_regex.match(line)
        if forward_matched is None:
            return ConcatenatedRegexParser.NO_MATCH
        forward_groups = forward_matched.groups()
        if self._is_last_group_matched(forward_groups):
            return self._extract_params_from_last_regex(forward_groups)
        backward_groups = self._backward_regex.match(line).groups()
        forward_matched_regex_name, only_one = self._check_that_only_one_regex_matched(
            forward_groups, backward_groups
        )
        regex_params = self._extract_regex_params_by_regex_name(
            forward_groups, forward_matched_regex_name, self._forward_parsers_indexes
        )
        extracted_regex_params = {forward_matched_regex_name: regex_params}
        if only_one:
            return extracted_regex_params
        return self._extract_params_from_many_matched_regexes(
            backward_groups, extracted_regex_params, forward_matched_regex_name, line
        )

    def _extract_params_from_many_matched_regexes(
        self, backward_groups, extracted_regex_params, forward_matched_regex_name, line
    ):
        backward_matched_regex_name = self._get_first_matched_parser_name(
            backward_groups, self._backward_group_index_to_regex
        )
        regex_params = self._extract_regex_params_by_regex_name(
            backward_groups, backward_matched_regex_name, self._backward_parsers_indexes
        )
        extracted_regex_params[backward_matched_regex_name] = regex_params
        left = self._numbers_in_list[forward_matched_regex_name] + 1
        right = self._numbers_in_list[backward_matched_regex_name] - 1
        self._brute_subregexes_matching(extracted_regex_params, left, right, line)
        return extracted_regex_params

    def _extract_regex_params_by_regex_name(self, groups, matched_regex_name, parsers_indexes):
        start_index = parsers_indexes[matched_regex_name][0]
        number_of_groups = parsers_indexes[matched_regex_name][1]
        regex_params = self._extract_regex_params(groups, number_of_groups, start_index)
        return regex_params

    def _get_first_matched_parser_name(self, groups, group_index_to_parser_name):
        for i in six.moves.range(len(groups)):
            if groups[i] is not None:
                first_matched = i
                break
        return group_index_to_parser_name[first_matched]

    def _check_that_only_one_regex_matched(self, forward_groups, backward_groups):
        regex_name = self._get_first_matched_parser_name(
            forward_groups, self._forward_group_index_to_regex
        )
        matched_regex_index = self._backward_parsers_indexes[regex_name][0]
        is_matched_one_regex = backward_groups[matched_regex_index] is not None
        return regex_name, is_matched_one_regex

    def _extract_params_from_last_regex(self, forward_groups):
        last_regex_name = self._parsers[-1].name
        last_regex_params = self._extract_regex_params_by_regex_name(
            forward_groups, last_regex_name, self._forward_parsers_indexes
        )
        return {last_regex_name: last_regex_params}

    def _is_last_group_matched(self, groups):
        return groups[-1] is not None

    def _extract_regex_params(self, groups, regex_group_number, regex_index):
        return tuple(
            groups[i]
            for i in six.moves.range(regex_index + 1, regex_index + regex_group_number + 1)
        )

    def _brute_subregexes_matching(self, extracted_regex_params, left, right, line):
        for i in six.moves.range(left, right + 1):
            match = self._parsers[i].get_regex_params(line)
            if match is not None:
                extracted_regex_params[self._parsers[i].name] = match
