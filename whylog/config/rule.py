from collections import defaultdict, deque
import itertools
from frozendict import frozendict
from abc import ABCMeta, abstractmethod

import six

from whylog.config.parsers import RegexParserFactory
from whylog.constraints.constraint_manager import ConstraintManager
from whylog.constraints.verifier import Verifier
from whylog.converters import CONVERTION_MAPPING


class Rule(object):
    EMPTY_BLACK_LIST = frozenset()
    LINKAGE_AND = "AND"
    LINKAGE_OR = "OR"
    LINKAGE_NOT = "NOT"

    LINKAGE_SELECTOR = {
        LINKAGE_AND: Verifier.constraints_and,
        LINKAGE_OR: Verifier.constraints_or,
        LINKAGE_NOT: Verifier.constraints_not
    }

    EFFECT_NUMBER = 0
    NO_RANGE = frozendict()
    DELTA_CONSTRAINTS = set(['time'])

    def __init__(self, causes, effect, constraints, linkage):
        self._causes = causes
        self._effect = effect
        self._constraints = constraints
        self._linkage = linkage
        self._frequency_information = self._gather_causes_frequency_information()

    def _gather_causes_frequency_information(self):
        """
        basing on self._causes and assumption that causes are sorted,
        produces list of pairs: (parser name, number of occurrences of this parser)
        """
        return [(elem.name, len(list(group))) for elem, group in itertools.groupby(self._causes)]

    def serialize(self):
        return {
            "causes": [
                cause.name for cause in self._causes
            ],
            "effect": self._effect.name,
            "constraints": self._constraints,
        }

    def get_new_parsers(self, parser_name_generator):
        new_parsers = []
        for parser in itertools.chain([self._effect], self._causes):
            # TODO: Refactor if teachers are mulithreding
            if parser_name_generator.is_free_parser_name(parser.name, self.EMPTY_BLACK_LIST):
                new_parsers.append(parser)
        return new_parsers

    def get_causes_parsers(self):
        return self._causes

    def get_effect_name(self):
        return self._effect.name

    def get_search_ranges(self, effect_clues):
        group, group_type = self._effect.get_primary_key_group()
        if not group:
            return self.NO_RANGE
        parser_ranges = self._calculate_parsers_ranges(effect_clues, group, group_type)
        if self._linkage == self.LINKAGE_OR:
            self.fix_ranges_for_unconnected_constraints(
                effect_clues, group, group_type, parser_ranges
            )
        return self._aggregate_by_log_type(parser_ranges)

    def fix_ranges_for_unconnected_constraints(
        self, effect_clues, group, group_type, parser_ranges
    ):
        for constraint in self._constraints:
            if constraint['name'] not in self.DELTA_CONSTRAINTS:
                parser_number = constraint['clues_groups'][0][0]
                converter = CONVERTION_MAPPING[group_type]
                primary_group_value = \
                    effect_clues[self.get_effect_name()].regex_parameters[group - 1]
                parser_ranges[parser_number][group_type]["left_bound"] = converter.MIN_VALUE
                parser_ranges[parser_number][group_type]["right_bound"] = primary_group_value

    def _calculate_parsers_ranges(self, effect_clues, group, group_type):
        parser_ranges = {
            self.EFFECT_NUMBER: self._get_effect_range(effect_clues, group, group_type)
        }
        queue = deque([self.EFFECT_NUMBER])
        aggregated_constraints = self._aggregate_constraints()
        used_parsers = set([self.EFFECT_NUMBER])
        while queue:
            parser_number = queue.popleft()
            for constraint in aggregated_constraints[parser_number]:
                clues_groups = constraint['clues_groups']
                depended_parser_number = clues_groups[0][0]
                base_parser_number = clues_groups[1][0]
                if depended_parser_number in used_parsers:
                    continue
                if not self._is_primary_key_constraint(clues_groups):
                    continue
                _, group_type = self._causes[depended_parser_number - 1].get_primary_key_group()
                parser_ranges[depended_parser_number] = self._calculate_parser_bounds(
                    base_parser_number, constraint['params'], group_type, parser_ranges
                )
                queue.append(depended_parser_number)
                used_parsers.add(depended_parser_number)
        self.create_ranges_for_unused_parsers(effect_clues, group, group_type, parser_ranges)
        parser_ranges.pop(self.EFFECT_NUMBER)
        return parser_ranges

    def create_ranges_for_unused_parsers(self, effect_clues, group, group_type, parser_ranges):
        for i in six.moves.range(len(self._causes)):
            if (i + 1) not in parser_ranges:
                converter = CONVERTION_MAPPING[group_type]
                primary_group_value = \
                    effect_clues[self.get_effect_name()].regex_parameters[group - 1]
                parser_ranges[(i + 1)] = {
                    group_type: {
                        'left_bound': converter.MIN_VALUE,
                        'right_bound': primary_group_value
                    }
                }

    def _get_effect_range(self, effect_clues, group, group_type):
        # Here assumption that len of primary_keys_groups equals 1
        primary_group_value = effect_clues[self.get_effect_name()].regex_parameters[group - 1]
        return {group_type: {"left_bound": primary_group_value, "right_bound": primary_group_value}}

    def _is_primary_key_constraint(self, clues_groups):
        base_parser_number = clues_groups[1][0]
        depended_parser_number = clues_groups[0][0]
        base_parser_group_number = clues_groups[1][1]
        depended_group_number = clues_groups[0][1]
        return self._is_primary_key_group(base_parser_group_number, base_parser_number) and \
               self._is_primary_key_group(depended_group_number, depended_parser_number)

    def _calculate_parser_bounds(self, base_parser_number, params, group_type, parser_ranges):
        max_delta = params.get('max_delta')
        min_delta = params.get('min_delta')
        left_bound, right_bound = self._get_base_bounds(
            base_parser_number, group_type, parser_ranges
        )
        converter = CONVERTION_MAPPING[group_type]
        new_left_bound = converter.switch_by_delta(left_bound, max_delta, "max")
        new_right_bound = converter.switch_by_delta(right_bound, min_delta, "min")
        return {group_type: {"left_bound": new_left_bound, "right_bound": new_right_bound}}

    @classmethod
    def _get_base_bounds(cls, base_parser_number, group_type, parser_ranges):
        left_bound = parser_ranges[base_parser_number][group_type]["left_bound"]
        right_bound = parser_ranges[base_parser_number][group_type]["right_bound"]
        return left_bound, right_bound

    def _aggregate_by_log_type(self, parser_ranges):
        search_ranges = {}
        for parser_number, ranges in six.iteritems(parser_ranges):
            parser_log_type = self._causes[parser_number - 1].log_type
            if parser_log_type not in search_ranges:
                search_ranges[parser_log_type] = ranges
                continue
            self._update_log_type_ranges(parser_log_type, ranges, search_ranges)
        return search_ranges

    def _update_log_type_ranges(self, parser_log_type, ranges, search_ranges):
        for group_type in ranges:
            if group_type not in search_ranges[parser_log_type]:
                search_ranges[parser_log_type][group_type] = ranges[group_type]
                continue
            self._update_bounds(search_ranges[parser_log_type][group_type], ranges[group_type])

    @classmethod
    def _update_bounds(cls, old_bounds_dict, parser_bound_dict):
        old_bounds_dict["left_bound"] = min(
            old_bounds_dict["left_bound"], parser_bound_dict["left_bound"]
        )
        old_bounds_dict["right_bound"] = max(
            old_bounds_dict["right_bound"], parser_bound_dict["right_bound"]
        )

    def _is_primary_key_group(self, parser_group_number, parser_number):
        if parser_number == self.EFFECT_NUMBER:
            return self._effect.is_primary_key(parser_group_number)
        return self._causes[parser_number - 1].is_primary_key(parser_group_number)

    def _aggregate_constraints(self):
        # Aggregate constraints have to have min_delta and max_delta params
        # At this moment only TimeConstraint has this property
        parser_with_constraints = defaultdict(list)
        for constraint in self._constraints:
            if constraint['name'] in self.DELTA_CONSTRAINTS:
                base_parser = constraint['clues_groups'][1][0]
                parser_with_constraints[base_parser].append(constraint)
        return parser_with_constraints

    def constraints_check(self, clues, effect_clues_dict):
        """
        check if given clues satisfy rule
        basing on its causes, effect and constraints.
        returns list of InvestigationResult objects
        """
        clues_lists = [
            (clues[parser_name], occurrences)
            for parser_name, occurrences in self._frequency_information
            if clues.get(parser_name) is not None
        ]
        effect_clue = effect_clues_dict[self._effect.name]
        constraint_manager = ConstraintManager()
        return self.LINKAGE_SELECTOR[self._linkage](
            clues_lists, effect_clue, self._constraints, constraint_manager
        )


@six.add_metaclass(ABCMeta)
class AbstractRuleFactory(object):
    @classmethod
    def create_from_intent(cls, user_rule_intent):
        parsers_dict = cls._create_parsers_from_intents(user_rule_intent)
        effect = parsers_dict.pop(user_rule_intent.effect_id)
        causes, parser_ids_mapper = cls._create_causes_list_with_clue_index(
            parsers_dict, user_rule_intent
        )
        constraints = cls._create_constraints_list(parser_ids_mapper, user_rule_intent)
        ordered_causes, modified_constraints = cls._order_causes_list(causes, constraints)
        # TODO use user_rule_intent instead of Rule.LINKAGE_AND when UserRuleIntent will support rule linkage
        return Rule(ordered_causes, effect, modified_constraints, Rule.LINKAGE_AND)

    @classmethod
    def _order_causes_list(cls, causes, constraints):
        causes_with_indexes = list(enumerate(causes, 1))
        causes_with_indexes.sort(key=lambda x: x[1].name)
        ordered_causes = []
        parser_index_mapping = {}
        for new_idx, (old_index, parser) in enumerate(causes_with_indexes, 1):
            ordered_causes.append(parser)
            parser_index_mapping[old_index] = new_idx
        for constraint in constraints:
            for clue_group in constraint['clues_groups']:
                if clue_group[0] != 0:
                    clue_group[0] = parser_index_mapping[clue_group[0]]
        return ordered_causes, constraints

    @classmethod
    @abstractmethod
    def _create_parsers_from_intents(cls, user_rule_intent):
        pass

    @classmethod
    def _create_causes_list_with_clue_index(cls, parsers_dict, user_rule_intent):
        parser_ids_mapper = {user_rule_intent.effect_id: 0}
        free_clue_index = 1
        causes = []
        for intent_id, parser in six.iteritems(parsers_dict):
            causes.append(parser)
            parser_ids_mapper[intent_id] = free_clue_index
            free_clue_index += 1
        return causes, parser_ids_mapper

    @classmethod
    def _create_constraints_list(cls, parser_ids_mapper, user_rule_intent):
        constraints = []
        for constraint_intent in user_rule_intent.constraints:
            clues = []
            for parser_id, group in constraint_intent.groups:
                cause_id = parser_ids_mapper[parser_id]
                clues.append([cause_id, group])
            constraint_dict = {
                "name": constraint_intent.type,
                "clues_groups": clues,
                "params": constraint_intent.params
            }
            constraints.append(constraint_dict)
        return constraints

    @classmethod
    def from_dao(cls, serialized_rule, parsers):
        # TODO: restore serialized_rule["linkage"] when UserRuleIntent will support rule linkage
        causes = [parsers[cause] for cause in serialized_rule["causes"]]
        return Rule(
            causes, parsers[serialized_rule["effect"]], serialized_rule["constraints"],
            serialized_rule.get("linkage", Rule.LINKAGE_AND)
        )


class RegexRuleFactory(AbstractRuleFactory):
    @classmethod
    def _create_parsers_from_intents(cls, user_rule_intent):
        return dict(
            (intent_id, RegexParserFactory.create_from_intent(parser_intent))
            for intent_id, parser_intent in six.iteritems(user_rule_intent.parsers)
        )
