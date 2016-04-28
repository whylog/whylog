import os.path
import platform

from whylog.config.consts import YamlFileNames


class ConfigPathFactory(object):
    @classmethod
    def get_path_to_config_files(cls, prefix_path, multi_platform=False):
        parsers_path = os.path.join(prefix_path, YamlFileNames.parsers)
        rules_path = os.path.join(prefix_path, YamlFileNames.rules)
        if multi_platform:
            if platform.system() == 'Windows':
                log_type_path = os.path.join(prefix_path, YamlFileNames.windows_log_types)
            else:
                log_type_path = os.path.join(prefix_path, YamlFileNames.unix_log_types)
        else:
            log_type_path = os.path.join(prefix_path, YamlFileNames.default_log_types)
        return [parsers_path, rules_path, log_type_path]
