from whylog.config.parsers import RegexParser

from abc import ABCMeta, abstractmethod
import uuid
import yaml


from whylog.config.parsers import RegexParser


class AbstractConfig(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_investigation_plan(self, front_input):
        pass


class YamlConfig(AbstractConfig):
    def __init__(self, parsers_path, rules_path, log_locations_path, log_type_manager=None):
        self._parsers_path = parsers_path
        self._rules_path = rules_path
        self._log_locations_path = log_locations_path

    def create_investigation_plan(self, front_input):
        pass

    def _get_log_type(self, front_input):
        pass

    def _find_matching_parsers(self, front_input, log_type):
        pass

    def _filter_rule_set(self, parsers_list):
        pass

    def _get_locations_for_logs(self, logs_types_list):
        pass

    def add_rule(self, user_rule_intent):
        rule = self._create_rule_from_user_rule_intent(user_rule_intent)
        rule_definition = rule.get_rule_in_form_to_save()
        parsers_definition = rule.get_rule_parsers_in_form_to_save()
        self._save_rule_definition(rule_definition)
        self._save_parsers_definition(parsers_definition)

    def _save_rule_definition(self, rule_definition):
        print yaml.dump(rule_definition)
        with open(self._rules_path, "a") as rules_file:
            rules_file.write(yaml.safe_dump(rule_definition))

    def _save_parsers_definition(self, parser_definitions):
        print parser_definitions
        print yaml.dump(parser_definitions)
        with open(self._parsers_path, "a") as parsers_file:
            parsers_file.write(yaml.safe_dump_all(parser_definitions))

    def _create_rule_from_user_rule_intent(self, user_rule_intent):
        parsers_dict = {
            intent_id: RegexParser(
                str(uuid.uuid4()), parser_intent.regex, parser_intent.primary_key_groups,
                parser_intent.log_type_name, parser_intent.data_conversions
            )
            for intent_id, parser_intent in user_rule_intent.parser_intents.iteritems()
        }
        effect = parsers_dict.get(user_rule_intent.effect_id)
        parsers_dict.pop(user_rule_intent.effect_id)
        parser_ids_mapper = {user_rule_intent.effect_id: 0}
        free_clue_index = 1
        causes = []
        for intent_id in parsers_dict:
            causes.append(parsers_dict.get(intent_id))
            parser_ids_mapper[intent_id] = free_clue_index
            free_clue_index += 1
        constraints = []
        for constraint_intent in user_rule_intent.constraint_intents:
            clues = [
                (parser_ids_mapper.get(parser_id), group)
                for (parser_id, group) in constraint_intent.groups
            ]
            constraint_dict = {"name": constraint_intent.type, "clues": clues}
            if constraint_intent.params is not None:
                constraint_dict["params"] = constraint_intent.params
            constraints.append(constraint_dict)
        return Rule(causes, effect, constraints)


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
        parser_definitions = [
            {
                "name": parser.name,
                "regex": parser.regex_str,
                "primary_key_groups": parser.primary_key_groups,
                "log_type": parser.log_type,
                "convertions": parser.convertions
            } for parser in self._causes
        ]
        parser_definitions.append(
            {
                "name": self._effect.name,
                "regex": self._effect.regex_str,
                "primary_key_groups": self._effect.primary_key_groups,
                "log_type": self._effect.log_type,
                "convertions": self._effect.convertions
            }
        )
        return parser_definitions


class InvestigationPlan(object):
    def __init__(self, front_input, rule_subset, log_location_dict):
        pass

    def get_next_investigation_step(self):
        pass


class RuleSubset(object):
    def __init__(self, rule_dict):
        pass

    def get_logs_types(self):
        pass

    def get_rules_for_log_type(self, log_type):
        pass

    def get_parsers_for_log_type(self, log_type):
        pass


class InvestigationStep(object):
    """
    Represents rules, parsers and locations of logs which are necessary
    to find and parse log files with potential causes.
    """

    def __init__(self, parsers, rules, log_location, effect_time):
        pass

    def get_clues(self, line):
        """
        Basing on parsers creates clues in investigation
        :param line: line from parsed file
        :returns: list of created clues
        """
        pass


class Clue(object):
    """
    Collects all the data that parser can extract from single log line.
    Also, contains parsed line and its source.
    """

    def __init__(self, regex_parameters, line_time, line_content, line_source):
        pass


class LogLocation(object):
    def __init__(self, filename_parser, log_type):
        pass
