from abc import ABCMeta, abstractmethod

import six
import yaml

from whylog.config.parsers import RegexParserFactory
from whylog.config.rule import RegexRuleFactory

from datetime import datetime

from whylog.config.log_type import LogType
from whylog.config.filename_matchers import RegexFilenameMatcher
from whylog.config.parsers import ConcatenatedRegexParser, RegexParser
from whylog.config.rule import Rule


@six.add_metaclass(ABCMeta)
class AbstractConfig(object):
    def __init__(self):
        self._parsers = self._load_parsers()
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

    def add_rule(self, user_rule_intent):
        created_rule = RegexRuleFactory.create_from_intent(user_rule_intent)
        self._save_rule_definition(created_rule.serialize())
        created_parsers = created_rule.get_new_parsers(self._parsers)
        self._save_parsers_definition(parser.serialize() for parser in created_parsers)
        self._rules.append(created_rule)
        for parser in created_parsers:
            self._parsers[parser.name] = parser

    def add_log_type(self, log_type):
        #TODO Can assume that exists only one LogType object for one log type name
        pass

    @abstractmethod
    def _save_rule_definition(self, rule_definition):
        pass

    @abstractmethod
    def _save_parsers_definition(self, parser_definitions):
        pass

    # mocked investigation plan for 003_match_time_range test
    def mocked_investigation_plan(self):
        matcher = RegexFilenameMatcher('localhost', 'node_1.log', 'default')
        default_log_type = LogType('default', [matcher])
        cause = RegexParser('cause', '^root cause$', [1], 'default', {1: 'date'})
        effect = RegexParser('effect', '^visible effect$', [1], 'default', {1: 'date'})
        concatenated = ConcatenatedRegexParser([cause])
        effect_time = datetime(2015, 12, 3, 12, 8, 9)
        earliest_cause_time = datetime(2015, 12, 3, 12, 8, 8)
        default_investigation_step = InvestigationStep(concatenated, effect_time, earliest_cause_time)
        rule = Rule([cause], effect, [{
            'clues_groups': [[1, 1], [0, 1]],
            'name': 'time',
            'params': {'max_delta': 1}
        }])
        return InvestigationPlan([], [(default_investigation_step, default_log_type)])

    def create_investigation_plan(self, front_input):
        return self.mocked_investigation_plan()

    def _get_log_type(self, front_input):
        pass

    def _find_matching_parsers(self, front_input, log_type):
        pass

    def _filter_rule_set(self, parsers_list):
        pass

    def _get_locations_for_logs(self, logs_types_list):
        pass


@six.add_metaclass(ABCMeta)
class AbstractFileConfig(AbstractConfig):
    def __init__(self, parsers_path, rules_path, log_type_path):
        self._parsers_path = parsers_path
        self._rules_path = rules_path
        self._log_type_path = log_type_path
        super(AbstractFileConfig, self).__init__()

    def _load_parsers(self):
        return dict(
            (parser_definition["name"], RegexParserFactory.from_dao(parser_definition))
            for parser_definition in self._load_file_with_config(self._parsers_path)
        )

    def _load_rules(self):
        return [
            RegexRuleFactory.from_dao(serialized_rule, self._parsers)
            for serialized_rule in self._load_file_with_config(self._rules_path)
        ]

    def _load_log_types(self):
        # return [
        #     LogTypeFactory.from_dao(serialized_log_type)
        #     for serialized_log_type in self._load_file_with_config(self._log_type_path)
        # ]
        pass

    @abstractmethod
    def _load_file_with_config(self, path):
        pass

    def _save_rule_definition(self, rule_definition):
        with open(self._rules_path, "a") as rules_file:
            rules_file.write(self._convert_rule_to_file_form(rule_definition))

    def _save_parsers_definition(self, parser_definitions):
        with open(self._parsers_path, "a") as parsers_file:
            parsers_file.write(self._convert_parsers_to_file_form(parser_definitions))

    @abstractmethod
    def _convert_rule_to_file_form(self, dict_definition):
        pass

    @abstractmethod
    def _convert_parsers_to_file_form(self, dict_definition):
        pass


class YamlConfig(AbstractFileConfig):
    def __init__(self, parsers_path, rules_path, log_type_path):
        super(YamlConfig, self).__init__(parsers_path, rules_path, log_type_path)

    def _load_file_with_config(self, path):
        with open(path, "r") as config_file:
            return list(yaml.load_all(config_file))

    def _convert_rule_to_file_form(self, rule_definition):
        return yaml.safe_dump(rule_definition, explicit_start=True)

    def _convert_parsers_to_file_form(self, parser_definitions):
        return yaml.safe_dump_all(parser_definitions, explicit_start=True)


class InvestigationPlan(object):
    def __init__(self, suspected_rules, investigation_metadata):
        self._suspected_rules = suspected_rules
        self._investigation_metadata = investigation_metadata

    def get_next_investigation_step_with_log_type(self):
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
    def __init__(self, concatenated_parser, effect_time, earliest_cause_time):
        self._concatenated_parser = concatenated_parser
        self.effect_time = effect_time
        self.earliest_cause_time = earliest_cause_time

    def get_clues(self, line, offset):
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

    def __init__(self, regex_parameters, line_time, line_prefix_content, line_source):
        pass
