import os.path


class ConfigPathFactory(object):
    @classmethod
    def get_path_to_config_files(cls, prefix_path):
        parsers_path = os.path.join(prefix_path, 'parsers.yaml')
        rules_path = os.path.join(prefix_path, 'rules.yaml')
        log_type_path = os.path.join(prefix_path, 'log_types.yaml')
        return [parsers_path, rules_path, log_type_path]
