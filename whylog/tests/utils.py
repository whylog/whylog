import os.path
import platform

from whylog.config.consts import YamlFileNames


class ConfigPathFactory(object):
    @classmethod
    def get_path_to_config_files(cls, prefix_path, multi_platform=True):
        parsers_path = os.path.join(prefix_path, YamlFileNames.parsers)
        rules_path = os.path.join(prefix_path, YamlFileNames.rules)
        if multi_platform:
            # log_types files contain path files patterns. In unix like systems directories in paths
            # are joined by '/', but in windows systems by '\'. It's reason by why we keeps separate files
            # for log types. It's usage only for test purposes.
            if platform.system() == 'Windows':
                log_types_file = YamlFileNames.windows_log_types
            else:
                log_types_file = YamlFileNames.unix_log_types
        else:
            log_types_file = YamlFileNames.default_log_types
        log_types_path = os.path.join(prefix_path, log_types_file)
        return [parsers_path, rules_path, log_types_path]
