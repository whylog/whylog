import os
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from datetime import datetime

import six
import yaml

from whylog.assistant.exceptions import UnsupportedAssistantError
from whylog.assistant.regex_assistant import RegexAssistant
from whylog.config.exceptions import UnsupportedFilenameMatcher
from whylog.config.filename_matchers import RegexFilenameMatcher, RegexFilenameMatcherFactory
from whylog.config.investigation_plan import Clue, InvestigationPlan, InvestigationStep, LineSource
from whylog.config.log_type import LogType
from whylog.config.parser_name_generator import ParserNameGenerator
from whylog.config.parsers import ConcatenatedRegexParser, RegexParserFactory
from whylog.config.rule import RegexRuleFactory


class AbstractConfigFactory(object):
    """
    This factory is responsible for finding .whylog directory (whylog config directory) and basing on
    found content directory creating object of subclass AbstractConfig. If not found then it creates minimal
    .whylog version in current directory.
    """
    WHYLOG_DIR = '.whylog'
    HOME_DIR = os.path.expanduser('~')
    ETC_DIR = '/etc'
    ASSISTANTS_DICT = {'regex': RegexAssistant}

    @classmethod
    @abstractmethod
    def load_config(cls, path):
        pass

    @classmethod
    def _attach_whylog_dir(cls, path):
        return os.path.join(path, cls.WHYLOG_DIR)

    @classmethod
    def _search_in_parents_directories(cls, path):
        if os.path.isdir(cls.WHYLOG_DIR):
            #current directory
            return path
        while True:
            path, suffix = os.path.split(path)
            if suffix == '':
                return None
            if os.path.isdir(cls._attach_whylog_dir(path)):
                return path

    @classmethod
    def _find_path_to_config(cls):
        path = cls._search_in_parents_directories(os.getcwd())
        if path is not None:
            return cls._attach_whylog_dir(path)
        dir_to_check = [cls._attach_whylog_dir(cls.HOME_DIR), cls._attach_whylog_dir(cls.ETC_DIR)]
        for directory in dir_to_check:
            if os.path.isdir(directory):
                return directory

    @classmethod
    def _create_empty_file(cls, path):
        open(path, 'w').close()

    @classmethod
    def _create_new_config_dir(cls, base_path):
        whylog_dir = cls._attach_whylog_dir(base_path)
        os.mkdir(whylog_dir, 0o755)
        config_paths = {}
        for key, file_name in six.iteritems(cls.FILES_NAMES):
            path = os.path.join(whylog_dir, file_name)
            cls._create_empty_file(path)
            config_paths[key] = path
        config_paths['pattern_assistant'] = 'regex'
        path_to_config = os.path.join(whylog_dir, cls.CONFIG_PATHS_FILE)
        return cls.create_file_with_config_paths(config_paths, path_to_config)

    @classmethod
    @abstractmethod
    def create_file_with_config_paths(cls, config_paths, path_to_config):
        pass

    @classmethod
    def get_config(cls):
        path = cls._find_path_to_config()
        if path is not None:
            path_to_config = os.path.join(path, cls.CONFIG_PATHS_FILE)
            return cls.load_config(path_to_config)
        path_to_config = cls._create_new_config_dir(os.getcwd())
        return cls.load_config(path_to_config)


class YamlConfigFactory(AbstractConfigFactory):
    CONFIG_PATHS_FILE = 'config.yaml'
    FILES_NAMES = {
        'parsers_path': 'parsers.yaml',
        'rules_path': 'rules.yaml',
        'log_types_path': 'log_types.yaml'
    }

    @classmethod
    def load_config(cls, path):
        with open(path, "r") as config_file:
            config_paths = yaml.load(config_file)
            assistant_name = config_paths.pop('pattern_assistant')
            assistant_class = cls.ASSISTANTS_DICT.get(assistant_name)
            if assistant_class is None:
                raise UnsupportedAssistantError(assistant_name)
            return YamlConfig(**config_paths), assistant_class

    @classmethod
    def create_file_with_config_paths(cls, config_paths, path_to_config):
        with open(path_to_config, 'w') as config_file:
            config_file.write(yaml.safe_dump(config_paths, explicit_start=True))
        return path_to_config


@six.add_metaclass(ABCMeta)
class AbstractConfig(object):
    words_count_in_name = 4

    def __init__(self):
        self._parsers = self._load_parsers()
        self._parsers_grouped_by_log_type = self._index_parsers_by_log_type(
            six.itervalues(
                self._parsers
            )
        )
        self._parser_name_generator = ParserNameGenerator(self._parsers)
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

    @classmethod
    def _index_parsers_by_log_type(cls, parsers):
        grouped_parsers = defaultdict(list)
        for parser in parsers:
            grouped_parsers[parser.log_type].append(parser)
        return grouped_parsers

    def add_rule(self, user_rule_intent):
        created_rule = RegexRuleFactory.create_from_intent(user_rule_intent)
        self._save_rule_definition(created_rule.serialize())
        created_parsers = created_rule.get_new_parsers(self._parser_name_generator)
        self._save_parsers_definition(parser.serialize() for parser in created_parsers)
        self._rules[created_rule.get_effect_name()].append(created_rule)
        for parser in created_parsers:
            self._parsers[parser.name] = parser

    def add_log_type(self, log_type):
        # TODO Can assume that exists only one LogType object for one log type name
        pass

    @abstractmethod
    def _save_rule_definition(self, rule_definition):
        pass

    @abstractmethod
    def _save_parsers_definition(self, parser_definitions):
        pass

    def create_investigation_plan(self, front_input, log_type):
        matching_parsers, effect_params = self._find_matching_parsers(
            front_input.line_content, log_type.name
        )
        suspected_rules = self._filter_rule_set(matching_parsers)
        concatenated_parsers = self._create_concatenated_parsers_for_investigation(suspected_rules)
        effect_clues = self._create_effect_clues(effect_params, front_input)
        steps = self._create_steps_in_investigation(
            concatenated_parsers, suspected_rules, effect_clues
        )
        return InvestigationPlan(suspected_rules, steps, effect_clues)

    def get_log_type(self, front_input):
        # TODO: remove mock
        matcher = RegexFilenameMatcher('localhost', 'node_1.log', 'default')
        return LogType('default', [matcher])

    def _create_effect_clues(self, effect_params, front_input):
        effect_clues = {}
        # TODO: remove mocks line source should come from front_input
        line_source = LineSource('localhost', 'node_1.log')
        for parser_name, params in six.iteritems(effect_params):
            parser = self._parsers[parser_name]
            clue = Clue(
                parser.convert_params(params), front_input.line_content, front_input.offset,
                line_source
            )
            effect_clues[parser_name] = clue
        return effect_clues

    def _find_matching_parsers(self, effect_line_content, log_type_name):
        """
        This method finding all parsers from Config base which matching with effect_line_content
        """
        matching_parsers = []
        extracted_params = {}
        for parser in self._parsers_grouped_by_log_type[log_type_name]:
            params = parser.get_regex_params(effect_line_content)
            if params is not None:
                extracted_params[parser.name] = params
                matching_parsers.append(parser)
        return matching_parsers, extracted_params

    def _filter_rule_set(self, parsers_list):
        """
        This method finding all rules from Config base which can be fulfilled in
        single investigation base on parsers_list found by _find_matching_parsers
        """
        suspected_rules = []
        for parser in parsers_list:
            rules = self._rules.get(parser.name)
            if rules is not None:
                suspected_rules.extend(rules)
        return suspected_rules

    @classmethod
    def _create_concatenated_parsers_for_investigation(cls, rules):
        """
        Create concatenated parser for all log types which participate in given investigation based
        on suspected rules found by _filter_rule_set
        """
        grouped_parsers = defaultdict(list)
        inserted_parsers = set()
        for suspected_rule in rules:
            for parser in suspected_rule.get_causes_parsers():
                if parser.name not in inserted_parsers:
                    grouped_parsers[parser.log_type].append(parser)
                    inserted_parsers.add(parser.name)
        return dict(
            (log_type_name, ConcatenatedRegexParser(parsers))
            for log_type_name, parsers in six.iteritems(grouped_parsers)
        )

    def _create_steps_in_investigation(self, concatenated_parsers, suspected_rules, effect_clues):
        steps = []
        for log_type_name, parser in six.iteritems(concatenated_parsers):
            log_type = self._log_types[log_type_name]
            #TODO mocked for 003_test
            #TODO calculate effect time(or other primary key value) and earliest cause time(or other primary key value)
            #TODO base on effect_clues and suspected_rules per log type
            effect_time = datetime(2015, 12, 3, 12, 8, 9)  #TODO remove mock
            earliest_cause_time = datetime(2015, 12, 3, 12, 8, 8)  #TODO remove mock
            investigation_step = InvestigationStep(parser, effect_time, earliest_cause_time)
            steps.append((investigation_step, log_type))
        return steps

    def is_free_parser_name(self, parser_name, black_list):
        return self._parser_name_generator.is_free_parser_name(parser_name, black_list)

    def propose_parser_name(self, line, regex_str, black_list):
        return self._parser_name_generator.propose_parser_name(
            line, regex_str, black_list, self.words_count_in_name
        )


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
        matchers_factory_dict = {'RegexFilenameMatcher': RegexFilenameMatcherFactory}
        for definition in matcher_definitions:
            matcher_class_name = definition['matcher_class_name']
            factory_class = matchers_factory_dict.get(matcher_class_name)
            if factory_class is None:
                raise UnsupportedFilenameMatcher(matcher_class_name)
            matcher = factory_class.from_dao(definition)
            matchers[definition['log_type_name']].append(matcher)
        return dict(
            (log_type_name, LogType(log_type_name, log_type_matchers))
            for log_type_name, log_type_matchers in matchers.items()
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

    @abstractmethod
    def _convert_rule_to_file_form(self, dict_definition):
        pass

    @abstractmethod
    def _convert_parsers_to_file_form(self, dict_definition):
        pass


class YamlConfig(AbstractFileConfig):
    def __init__(self, parsers_path, rules_path, log_types_path):
        super(YamlConfig, self).__init__(parsers_path, rules_path, log_types_path)

    def _load_file_with_config(self, path):
        with open(path, "r") as config_file:
            return list(yaml.load_all(config_file))

    def _convert_rule_to_file_form(self, rule_definition):
        return yaml.safe_dump(rule_definition, explicit_start=True)

    def _convert_parsers_to_file_form(self, parser_definitions):
        return yaml.safe_dump_all(parser_definitions, explicit_start=True)


class RuleSubset(object):
    def __init__(self, rule_dict):
        pass

    def get_logs_types(self):
        pass

    def get_rules_for_log_type(self, log_type):
        pass

    def get_parsers_for_log_type(self, log_type):
        pass
