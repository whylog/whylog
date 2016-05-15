import yaml

from whylog.config.abstract_file_config import AbstractFileConfig


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

    def _convert_matcher_to_file_form(self, matcher_definition):
        return yaml.safe_dump(matcher_definition, explicit_start=True)
