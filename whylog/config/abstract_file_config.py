from abc import ABCMeta, abstractmethod
from collections import defaultdict

import six

from whylog.config.abstract_config import AbstractConfig
from whylog.config.exceptions import UnsupportedFilenameMatcher
from whylog.config.filename_matchers import WildCardFilenameMatcherFactory
from whylog.config.log_type import LogType
from whylog.config.parsers import RegexParserFactory
from whylog.config.rule import RegexRuleFactory


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
        loaded_rules = defaultdict(list)
        for serialized_rule in self._load_file_with_config(self._rules_path):
            rule = RegexRuleFactory.from_dao(serialized_rule, self._parsers)
            loaded_rules[serialized_rule["effect"]].append(rule)
        return loaded_rules

    def _load_log_types(self):
        matchers = defaultdict(list)
        matcher_definitions = self._load_file_with_config(self._log_type_path)
        matchers_factory_dict = {'WildCardFilenameMatcher': WildCardFilenameMatcherFactory}
        for definition in matcher_definitions:
            matcher_class_name = definition['matcher_class_name']
            factory_class = matchers_factory_dict.get(matcher_class_name)
            if factory_class is None:
                raise UnsupportedFilenameMatcher(matcher_class_name)
            matcher = factory_class.from_dao(definition)
            matchers[definition['log_type_name']].append(matcher)
        return dict(
            (log_type_name, LogType(log_type_name, log_type_matchers))
            for log_type_name, log_type_matchers in six.iteritems(matchers)
        )

    @abstractmethod
    def _load_file_with_config(self, path):
        pass

    def _save_rule_definition(self, rule_definition):
        with open(self._rules_path, "a") as rules_file:
            rules_file.write(self._convert_rule_to_file_form(rule_definition))

    def _save_parsers_definition(self, parser_definitions):
        with open(self._parsers_path, "a") as parsers_file:
            parsers_file.write(self._convert_parsers_to_file_form(parser_definitions))

    def _save_filename_matcher_definition(self, matcher_definition):
        with open(self._log_type_path, "a") as parsers_file:
            parsers_file.write(self._convert_matcher_to_file_form(matcher_definition))

    def _resave_all_log_types(self, matchers_definition):
        with open(self._log_type_path, "w") as parsers_file:
            parsers_file.write(self._massive_dump_to_yaml(matchers_definition))

    def _resave_all_parsers(self, parsers_definition):
        with open(self._parsers_path, "w") as parsers_file:
            parsers_file.write(self._massive_dump_to_yaml(parsers_definition))

    @abstractmethod
    def _massive_dump_to_yaml(self, definition):
        pass

    @abstractmethod
    def _convert_rule_to_file_form(self, dict_definition):
        pass

    @abstractmethod
    def _convert_parsers_to_file_form(self, dict_definition):
        pass

    @abstractmethod
    def _convert_matcher_to_file_form(self, dict_definition):
        pass
