import os.path


class ConfigPathFactory(object):
    @classmethod
    def get_path_to_config_files(cls, directories_in_path):
        path = os.path.join(*directories_in_path)
        parsers_path = os.path.join(path, 'parsers.yaml')
        rules_path = os.path.join(path, 'rules.yaml')
        log_type_path = os.path.join(path, 'log_types.yaml')
        return [parsers_path, rules_path, log_type_path]
