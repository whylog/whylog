from collections import defaultdict, deque
import itertools
from frozendict import frozendict
from abc import ABCMeta, abstractmethod

import six

from whylog.config.parsers import RegexParserFactory
from whylog.constraints.constraint_manager import ConstraintManager
from whylog.constraints.verifier import Verifier


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
        # if self._linkage != self.LINKAGE_AND:
        # TODO: implementation for OR linkage
        # raise NotImplementedError
        group, group_type = self._effect.get_primary_key_group()
        if not group:
            return self.NO_RANGE
        # Here assumption that len of primary_keys_groups equals 1
        primary_group_value = effect_clues[self.get_effect_name()].regex_parameters[group - 1]
        parser_ranges = {
            self.EFFECT_NUMBER: {group_type: {"left_bound": primary_group_value, "right_bound": primary_group_value}}}
        queue = deque([self.EFFECT_NUMBER])
        aggregated_constraints = self._aggregate_constraints()
        while queue:
            parser_number = queue.popleft()
            for constraint in aggregated_constraints[parser_number]:
                constraint_type = constraint['name']
                depended_parser_number = constraint['clues_groups'][0][0]
                depended_group_number = constraint['clues_groups'][0][1]
                base_parser_number = constraint['clues_groups'][1][0]
                base_parser_group_number = constraint['clues_groups'][1][1]
                in_primary_key = self._is_primary_key_group(base_parser_group_number, base_parser_number)
                if not in_primary_key:
                    continue
                max_delta = constraint['params'].get('max_delta')
                min_delta = constraint['params'].get('min_delta', 0)
                # depended_group_type = self
                # parser_ranges[depended_parser_number][]
                queue.append(depended_parser_number)

    def _is_primary_key_group(self, base_parser_group_number, base_parser_number):
        if base_parser_number == self.EFFECT_NUMBER:
            return self._effect.is_primary_key(base_parser_group_number)
        return self._causes[base_parser_number - 1].is_primary_key(base_parser_group_number)

    def _aggregate_constraints(self):
        # Aggregate constraints have to have min_delta and max_delta params
        # At this moment only TimeConstraint has this property
        delta_constraints = set(['time'])
        parser_with_constraints = defaultdict(list)
        for constraint in self._constraints:
            if constraint['name'] in delta_constraints:
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
