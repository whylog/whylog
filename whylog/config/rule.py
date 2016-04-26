import itertools
from abc import ABCMeta, abstractmethod

import six

from whylog.config.parsers import RegexParserFactory
from whylog.constraints.verifier import Verifier


class Rule(object):
    EMPTY_BLACK_LIST = frozenset()

    def __init__(self, causes, effect, constraints):
        self._causes = causes
        self._effect = effect
        self._constraints = constraints

    def serialize(self):
        return {
            "causes": [cause.name for cause in self._causes],
            "effect": self._effect.name,
            "constraints": self._constraints,
        }

    def get_new_parsers(self, parser_name_generator):
        new_parsers = []
        for parser in itertools.chain([self._effect], self._causes):
            #TODO: Refactor if teachers are mulithreding
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
        clues_lists = [clues[cause.name] for cause in self._causes if cause.name in clues]
        effect_clue = effect_clues_dict[self._effect.name]
        return Verifier.constraints_and(clues_lists, effect_clue, self._constraints)


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
        return Rule(causes, effect, constraints)

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
                clues.append((cause_id, group))
            constraint_dict = {
                "name": constraint_intent.type,
                "clues_groups": clues,
                "params": constraint_intent.params
            }
            constraints.append(constraint_dict)
        return constraints

    @classmethod
    def from_dao(cls, serialized_rule, parsers):
        return Rule(
            [parsers[cause] for cause in serialized_rule["causes"]],
            parsers[serialized_rule["effect"]], serialized_rule["constraints"]
        )


class RegexRuleFactory(AbstractRuleFactory):
    @classmethod
    def _create_parsers_from_intents(cls, user_rule_intent):
        return dict(
            (
                intent_id, RegexParserFactory.create_from_intent(parser_intent)
            ) for intent_id, parser_intent in six.iteritems(user_rule_intent.parsers)
        )
