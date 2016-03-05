import itertools

from whylog.config.parsers import RegexParserFactory


class Rule(object):
    def __init__(self, causes, effect, constraints):
        self._causes = causes
        self._effect = effect
        self._constraints = constraints

    def serialize_rule(self):
        return {
            "causes": [cause.name for cause in self._causes],
            "effect": self._effect.name if self._effect is not None else None,
            "constraints": self._constraints,
        }

    def serialize_parsers(self):
        if self._effect is not None:
            effect_list = [self._effect]
        else:
            effect_list = []
        return [parser.serialize_parser() for parser in itertools.chain(self._causes, effect_list)]


class RuleFactory(object):
    @classmethod
    def create_rule_from_user_rule_intent(cls, user_rule_intent):
        parsers_dict = cls._create_parsers_from_parsers_intents(user_rule_intent)
        effect = None
        if user_rule_intent.effect_id is not None:
            effect = parsers_dict.pop(user_rule_intent.effect_id)
        causes, parser_ids_mapper = cls._create_causes_list_with_clue_index(
            parsers_dict, user_rule_intent
        )
        constraints = cls._create_constraints_list(parser_ids_mapper, user_rule_intent)
        return Rule(causes, effect, constraints)

    @classmethod
    def _create_parsers_from_parsers_intents(cls, user_rule_intent):
        return dict(
            (
                intent_id, RegexParserFactory.create_from_intent(parser_intent)
            ) for intent_id, parser_intent in user_rule_intent.parsers.items()
        )

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
            constraint_dict = {
                "name": constraint_intent.type,
                "clues": clues,
                "params": constraint_intent.params
            }
            constraints.append(constraint_dict)
        return constraints
