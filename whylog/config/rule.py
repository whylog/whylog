from whylog.config.parsers import RegexParserFactory


class Rule(object):
    def __init__(self, causes, effect, constraints):
        self._causes = causes
        self._effect = effect
        self._constraints = constraints

    def get_rule_in_form_to_save(self):
        return {
            "causes": [cause.name for cause in self._causes],
            "effect": self._effect.name,
            "constraints": self._constraints
        }

    def get_rule_parsers_in_form_to_save(self):
        return [
            {
                "name": parser.name,
                "regex": parser.regex_str,
                "primary_key_groups": parser.primary_key_groups,
                "log_type": parser.log_type,
                "convertions": parser.convertions
            } for parser in self._causes + [self._effect]
        ]


class RuleFactory(object):
    @classmethod
    def create_rule_from_user_rule_intent(cls, user_rule_intent):
        parsers_dict = cls._create_parsers_from_parsers_intents(user_rule_intent)
        effect = parsers_dict.get(user_rule_intent.effect_id)
        parsers_dict.pop(user_rule_intent.effect_id)
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
        for intent_id in parsers_dict:
            causes.append(parsers_dict.get(intent_id))
            parser_ids_mapper[intent_id] = free_clue_index
            free_clue_index += 1
        return causes, parser_ids_mapper

    @classmethod
    def _create_constraints_list(cls, parser_ids_mapper, user_rule_intent):
        constraints = []
        for constraint_intent in user_rule_intent.constraints:
            clues = [
                (parser_ids_mapper.get(parser_id), group)
                for (parser_id, group) in constraint_intent.groups
            ]
            constraint_dict = {"name": constraint_intent.type, "clues": clues}
            if bool(constraint_intent.params):
                constraint_dict["params"] = constraint_intent.params
            constraints.append(constraint_dict)
        return constraints
