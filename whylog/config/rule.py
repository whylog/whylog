import itertools
from abc import ABCMeta, abstractmethod

import six

from whylog.config.parsers import RegexParserFactory


class Rule(object):
    def __init__(self, causes, effect, constraints):
        self._causes = causes
        self._effect = effect
        self._constraints = constraints

    def to_data_access_object_form(self):
        return RuleDAO([cause.name for cause in self._causes], self._effect.name, self._constraints)

    def get_new_parsers(self, old_parsers):
        new_parsers = []
        for parser in itertools.chain([self._effect], self._causes):
            if old_parsers.get(parser.name) is None:
                new_parsers.append(parser)
        return new_parsers


class RuleDAO(object):
    def __init__(self, causes, effect, constraints):
        self.causes = causes
        self.effect = effect
        self.constraints = constraints

    def create_rule(self, parsers):
        return Rule([parsers[cause]
                     for cause in self.causes], parsers[self.effect], self.constraints)


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
                cause_id = parser_ids_mapper[parser_id]
                clues.append((cause_id, group))
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
