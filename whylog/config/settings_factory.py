import os
from abc import abstractmethod

import six
import yaml

from whylog.config.consts import YamlFileNames


class AbstractSettingsFactory(object):
    """
    Note: This class use yaml format. Here is assumption that in every .whylog dir we have a
    settings settings.yaml file. Which has all data that enable creating subclass AbstractConfig object and
    subclass AbstractAssistant. No matter what kind of config was saved in settings.yaml.
    """
    DEFAULT_PATTERN_ASSISTANT = 'regex'

    @classmethod
    def create_new_settings_dir(cls, base_path, whylog_dir, settings_file):
        whylog_dir = os.path.join(base_path, whylog_dir)
        os.mkdir(whylog_dir, 0o755)
        settings = cls._create_settings_dict(whylog_dir)
        path_to_settings = os.path.join(whylog_dir, settings_file)
        return cls._create_settings_file(settings, path_to_settings)

    @classmethod
    def _create_empty_file(cls, path):
        open(path, 'w').close()

    @classmethod
    def _create_settings_file(cls, config_paths, path_to_config):
        with open(path_to_config, 'w') as config_file:
            config_file.write(yaml.safe_dump(config_paths, explicit_start=True))
        return path_to_config

    @classmethod
    @abstractmethod
    def _create_settings_dict(cls, whylog_dir):
        pass


class YamlSettingsFactory(AbstractSettingsFactory):
    FILES_NAMES = {
        'parsers_path': YamlFileNames.parsers,
        'rules_path': YamlFileNames.rules,
        'log_types_path': YamlFileNames.default_log_types,
    }

    @classmethod
    def _create_settings_dict(cls, whylog_dir):
        settings = {}
        for key, file_name in six.iteritems(cls.FILES_NAMES):
            path = os.path.join(whylog_dir, file_name)
            cls._create_empty_file(path)
            settings[key] = path
        settings['pattern_assistant'] = cls.DEFAULT_PATTERN_ASSISTANT
        settings['config_type'] = 'yaml'
        return settings
