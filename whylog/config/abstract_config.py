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
    DEFAULT_NAME = "default"
    DEFAULT_LOG_TYPE = LogType(
        DEFAULT_NAME, [
            WildCardFilenameMatcher("localhost", "", DEFAULT_NAME, RegexSuperParser("", [], {}))
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
            self._parsers_grouped_by_log_type[parser.log_type].append(parser)
        self._parser_name_generator = ParserNameGenerator(self._parsers)

    def add_log_type(self, log_type):
        for matcher in log_type.filename_matchers:
            self.add_filename_matcher_to_log_type(matcher)
        self._log_types[log_type.name] = log_type

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
        if self.DEFAULT_NAME in self._log_types:
            return six.itervalues(self._log_types)
        return itertools.chain([self.DEFAULT_LOG_TYPE], six.itervalues(self._log_types))

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

    @classmethod
    def _get_search_ranges(cls, suspected_rules, effect_clues):
        """
        old_search_range is a dictionary with two keys: InvesitgationStep.LEFT_BOUND and
        InvesitgationStep.RIGHT_BOUND. Values in this dict are concrete values of type the same as type of some
        primary key. Both values taken together represent some interval.
        Sample search range:
            {
                InvesitgationStep.LEFT_BOUND: datetime(2016, 5, 29, 12, 33, 0),
                InvesitgationStep.RIGHT_BOUND: datetime(2016, 5, 29, 12, 33, 30)
            }
        Log type's search ranges in rule context is a dictionary with old_search_range for every type of primary key of
        rule's parsers that belong to this log type.
        Sample log type's search ranges:
            {
                'date': {
                    InvesitgationStep.LEFT_BOUND: datetime(2016, 5, 29, 12, 33, 0),
                    InvesitgationStep.RIGHT_BOUND: datetime(2016, 5, 29, 12, 33, 30)
                }
            }
        Rule's search_ranges is sum of all log type's search ranges, where rule's parsers belong to these log types.
        Sample rule's search ranges (1) : {
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
        Sample rule's search ranges (2) : {
            'apache': {
                'date': {
                    InvesitgationStep.LEFT_BOUND: datetime(2016, 5, 29, 12, 32, 0),
                    InvesitgationStep.RIGHT_BOUND: datetime(2016, 5, 29, 12, 33, 20)
                }
            },
        }
        This method sums all rule's search ranges from every rule in suspected rules.
        Expected returned value based on (1) and (2): {
            'apache': {
                'date': {
                    InvesitgationStep.LEFT_BOUND: datetime(2016, 5, 29, 12, 32, 0),
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
        """
        # This implementation assumes that all primary key groups is a one element list
        # TODO implementation for longer primary key groups
        search_ranges = {}
        for rule in suspected_rules:
            rule_search_ranges = rule.get_search_ranges(effect_clues)
            for log_type_name, log_type_ranges in six.iteritems(rule_search_ranges):
                log_type_search_range = search_ranges.get(log_type_name)
                if log_type_search_range is None:
                    search_ranges[log_type_name] = log_type_ranges
                    continue
                for type, range in six.iteritems(rule_search_ranges[log_type_name]):
                    old_search_range = log_type_search_range.get(type)
                    if old_search_range is None:
                        log_type_search_range[type] = range
                        continue
                    left_bound, right_bound = cls._calculate_new_bounds(range, old_search_range)
                    old_search_range[InvestigationStep.LEFT_BOUND] = left_bound
                    old_search_range[InvestigationStep.RIGHT_BOUND] = right_bound
        return search_ranges

    @classmethod
    def _calculate_new_bounds(cls, range, old_search_range):
        left_bound_candidate = range[InvestigationStep.LEFT_BOUND]
        right_bound_candidate = range[InvestigationStep.RIGHT_BOUND]
        left_bound = old_search_range[InvestigationStep.LEFT_BOUND]
        right_bound = old_search_range[InvestigationStep.RIGHT_BOUND]
        return min(left_bound_candidate, left_bound), max(right_bound_candidate, right_bound)

    def is_free_parser_name(self, parser_name, black_list):
        return self._parser_name_generator.is_free_parser_name(parser_name, black_list)

    def propose_parser_name(self, line, regex_str, black_list):
        return self._parser_name_generator.propose_parser_name(
            line, regex_str, black_list, self.words_count_in_name
        )
