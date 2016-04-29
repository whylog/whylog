import os.path
from whylog.config.consts import YamlFileNames


class ConfigPathFactory(object):
    @classmethod
    def get_path_to_config_files(cls, prefix_path):
        parsers_path = os.path.join(prefix_path, YamlFileNames.parsers)
        rules_path = os.path.join(prefix_path, YamlFileNames.rules)
        log_type_path = os.path.join(prefix_path, YamlFileNames.log_types)
        return [parsers_path, rules_path, log_type_path]
