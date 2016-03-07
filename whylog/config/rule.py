import itertools
from abc import ABCMeta, abstractmethod

import six

from whylog.config.parser_exceptions import InvalidParserIndex
from whylog.config.parsers import RegexParserFactory


class Rule(object):
    def __init__(self, causes, effect, constraints):
        self._causes = causes
        self._effect = effect
        self._constraints = constraints

    def serialize_rule(self):
        return {
            "causes": [cause.name for cause in self._causes],
            "effect": self._effect.name,
            "constraints": self._constraints,
        }

    def serialize_parsers(self):
        return [
            parser.serialize_parser() for parser in itertools.chain(self._causes, [self._effect])
        ]


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
        for intent_id, parser in parsers_dict.items():
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
                cause_id = parser_ids_mapper.get(parser_id)
                if cause_id is not None:
                    clues.append((cause_id, group))
                else:
                    raise InvalidParserIndex(parser_id)
            constraint_dict = {
                "name": constraint_intent.type,
                "clues_groups": clues,
                "params": constraint_intent.params
            }
            constraints.append(constraint_dict)
        return constraints


class RegexRuleFactory(AbstractRuleFactory):
    @classmethod
    def _create_parsers_from_intents(cls, user_rule_intent):
        return dict(
            (
                intent_id, RegexParserFactory.create_from_intent(parser_intent)
            ) for intent_id, parser_intent in user_rule_intent.parsers.items()
        )
