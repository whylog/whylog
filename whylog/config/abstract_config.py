import itertools
from abc import ABCMeta, abstractmethod
from collections import defaultdict

import six

from whylog.config.filename_matchers import WildCardFilenameMatcher
from whylog.config.investigation_plan import Clue, InvestigationPlan, InvestigationStep
from whylog.config.log_type import LogType
from whylog.config.parser_name_generator import ParserNameGenerator
from whylog.config.parser_subset import ConcatenatedRegexParser
from whylog.config.rule import RegexRuleFactory
from whylog.config.super_parser import RegexSuperParser


@six.add_metaclass(ABCMeta)
class AbstractConfig(object):
    words_count_in_name = 4
    DEFAULT_LOG_TYPE = LogType(
        "default", [
            WildCardFilenameMatcher("", "", "default", RegexSuperParser("", [], {}))
        ]
    ) # yapf: disable

    def __init__(self):
        self._parsers = self._load_parsers()
        self._parsers_grouped_by_log_type = self._index_parsers_by_log_type(
            six.itervalues(self._parsers)
        )
        self._parser_name_generator = ParserNameGenerator(self._parsers)
        self._rules = self._load_rules()
        self._log_types = self._load_log_types()

    @abstractmethod
    def _load_parsers(self):
        pass

    @abstractmethod
    def _load_rules(self):
        pass

    @abstractmethod
    def _load_log_types(self):
        pass

    @classmethod
    def _index_parsers_by_log_type(cls, parsers):
        grouped_parsers = defaultdict(list)
        for parser in parsers:
            grouped_parsers[parser.log_type].append(parser)
        return grouped_parsers

    def add_rule(self, user_rule_intent):
        created_rule = RegexRuleFactory.create_from_intent(user_rule_intent)
        self._save_rule_definition(created_rule.serialize())
        created_parsers = created_rule.get_new_parsers(self._parser_name_generator)
        self._save_parsers_definition(parser.serialize() for parser in created_parsers)
        self._rules[created_rule.get_effect_name()].append(created_rule)
        for parser in created_parsers:
            self._parsers[parser.name] = parser

    def add_log_type(self, log_type):
        for matcher in log_type.filename_matchers:
            self.add_filename_matcher_to_log_type(matcher)

    def add_filename_matcher_to_log_type(self, matcher):
        self._save_filename_matcher_definition(matcher.serialize())

    @abstractmethod
    def _save_rule_definition(self, rule_definition):
        pass

    @abstractmethod
    def _save_parsers_definition(self, parser_definitions):
        pass

    @abstractmethod
    def _save_filename_matcher_definition(self, matcher_definition):
        pass

    def get_all_log_types(self):
        return itertools.chain(self.DEFAULT_LOG_TYPE, six.itervalues(self._log_types))

    def get_log_type(self, line_source):
        for log_type in six.itervalues(self._log_types):
            if line_source in log_type:
                return log_type

    def create_investigation_plan(self, front_input, log_type):
        matching_parsers, effect_params = self._find_matching_parsers(
            front_input.line_content, log_type.name
        )
        suspected_rules = self._filter_rule_set(matching_parsers)
        concatenated_parsers = self._create_concatenated_parsers_for_investigation(suspected_rules)
        effect_clues = self._create_effect_clues(effect_params, front_input)
        steps = self._create_steps_in_investigation(
            concatenated_parsers, suspected_rules, effect_clues
        )
        return InvestigationPlan(suspected_rules, steps, effect_clues)

    def _create_effect_clues(self, effect_params, front_input):
        effect_clues = {}
        for parser_name, params in six.iteritems(effect_params):
            parser = self._parsers[parser_name]
            clue = Clue(
                parser.convert_params(
                    params
                ), front_input.line_content, front_input.offset, front_input.line_source
            )  # yapf: disable
            effect_clues[parser_name] = clue
        return effect_clues

    def _find_matching_parsers(self, effect_line_content, log_type_name):
        """
        This method finding all parsers from Config base which matching with effect_line_content
        """
        matching_parsers = []
        extracted_params = {}
        for parser in self._parsers_grouped_by_log_type[log_type_name]:
            params = parser.get_regex_params(effect_line_content)
            if params is not None:
                extracted_params[parser.name] = params
                matching_parsers.append(parser)
        return matching_parsers, extracted_params

    def _filter_rule_set(self, parsers_list):
        """
        This method finding all rules from Config base which can be fulfilled in
        single investigation base on parsers_list found by _find_matching_parsers
        """
        suspected_rules = []
        for parser in parsers_list:
            rules = self._rules.get(parser.name)
            if rules is not None:
                suspected_rules.extend(rules)
        return suspected_rules

    @classmethod
    def _create_concatenated_parsers_for_investigation(cls, rules):
        """
        Create concatenated parser for all log types which participate in given investigation based
        on suspected rules found by _filter_rule_set
        """
        grouped_parsers = defaultdict(list)
        inserted_parsers = set()
        for suspected_rule in rules:
            for parser in suspected_rule.get_causes_parsers():
                if parser.name not in inserted_parsers:
                    grouped_parsers[parser.log_type].append(parser)
                    inserted_parsers.add(parser.name)
        return dict(
            (log_type_name, ConcatenatedRegexParser(parsers))
            for log_type_name, parsers in six.iteritems(grouped_parsers)
        )

    def _create_steps_in_investigation(self, concatenated_parsers, suspected_rules, effect_clues):
        steps = []
        search_ranges = self._get_search_ranges(suspected_rules, effect_clues)
        for log_type_name, parser in six.iteritems(concatenated_parsers):
            log_type = self._log_types[log_type_name]
            investigation_step = InvestigationStep(parser, search_ranges.get(log_type_name, {}))
            steps.append((investigation_step, log_type))
        return steps

    def _get_search_ranges(self, suspected_rules, effect_clues):
        """
        Search range is a dictionary with two keys InvesitgationStep.LEFT_BOUND and
        InvesitgationStep.RIGHT_BOUND. Values in this dict are concrete value that
        represents interval of primary key values. This interval can be map to
        interval of offsets in file that has compatible primary key with concrete search range.
        It allowed to cut out lines in parsed file, without parsing every single line.
        This method basing on search ranges from suspected rules calculates
        search ranges for every primary key type that can be predicted. Returned search ranges are
        grouped by log type.
        Sample search ranges: {
            'apache': {
                'date': {
                    InvesitgationStep.LEFT_BOUND: datetime(2016, 5, 29, 12, 33, 0),
                    InvesitgationStep.RIGHT_BOUND: datetime(2016, 5, 29, 12, 33, 30)
                }
            },
            'database': {
                'date': {
                    InvesitgationStep.LEFT_BOUND: datetime(2016, 5, 29, 12, 32, 0),
                    InvesitgationStep.RIGHT_BOUND: datetime(2016, 5, 29, 12, 33, 20)
                }
            }
        }
        Meaning of this search ranges:
        Algorithm returns ranges only for two log types: apache i database.
        For every log type calculated range only for files with primary key
        based on date. Values in range for apache log type means that LogReader
        must only parse lines in compatible files these has a date between datetime(2016, 5, 29, 12, 33, 0)
        and datetime(2016, 5, 29, 12, 33, 30)
        """
        # This implementation assumes that all primary key groups is a one element list
        # TODO implementation for longer primary key groups
        search_ranges = {}
        for rule in suspected_rules:
            rule_search_ranges = rule.get_search_ranges(effect_clues)
            for log_type_name, log_type_ranges in six.iteritems(rule_search_ranges):
                if log_type_name not in search_ranges:
                    search_ranges[log_type_name] = log_type_ranges
                    continue
                for key_type, type_range in six.iteritems(rule_search_ranges[log_type_name]):
                    if key_type not in search_ranges[log_type_name]:
                        search_ranges[log_type_name][key_type] = type_range
                        continue
                    left_bound_candidate = type_range['left_bound']
                    right_bound_candidate = type_range['right_bound']
                    left_bound = search_ranges[log_type_name][key_type]['left_bound']
                    right_bound = search_ranges[log_type_name][key_type]['right_bound']
                    search_ranges[log_type_name][key_type]['left_bound'] = min(
                        left_bound, left_bound_candidate
                    )
                    search_ranges[log_type_name][key_type]['right_bound'] = max(
                        right_bound, right_bound_candidate
                    )
        return search_ranges

    def is_free_parser_name(self, parser_name, black_list):
        return self._parser_name_generator.is_free_parser_name(parser_name, black_list)

    def propose_parser_name(self, line, regex_str, black_list):
        return self._parser_name_generator.propose_parser_name(
            line, regex_str, black_list, self.words_count_in_name
        )
