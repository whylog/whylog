import itertools
from abc import ABCMeta, abstractmethod

import six

from whylog.config.parsers import RegexParserFactory
from whylog.constraints.verifier import ConstraintManager, Verifier


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
