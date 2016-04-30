import os
from abc import abstractmethod

import six
import yaml

from whylog.assistant.exceptions import UnsupportedAssistantError
from whylog.assistant.regex_assistant import RegexAssistant
from whylog.config.consts import YamlFileNames
from whylog.config.exceptions import UnsupportedConfigType
from whylog.config.yaml_config import YamlConfig


class AbstractSettingsFactory(object):
    """
    Note: This class use yaml format. Here is assumption that in every .whylog dir we have a
    settings settings.yaml file. Which has all data that enable creating subclass AbstractConfig object and
    subclass AbstractAssistant. No matter what kind of config was saved in settings.yaml.
    """
    DEFAULT_PATTERN_ASSISTANT = 'regex'

    @classmethod
    def create_new_settings_dir(cls, base_path):
        whylog_dir = os.path.join(base_path, SettingsFactorySelector.WHYLOG_DIR)
        os.mkdir(whylog_dir, 0o755)
        settings = cls._create_settings_dict(whylog_dir)
        path_to_settings = os.path.join(whylog_dir, SettingsFactorySelector.CONFIG_SETTINGS_FILE)
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


class SettingsFactorySelector(object):
    """
    This class is responsible for finding .whylog directory (whylog settings directory) and basing on
    found content directory creating settings. If not found then it creates minimal
    .whylog version in current directory.
    """
    WHYLOG_DIR = '.whylog'
    CONFIG_SETTINGS_FILE = YamlFileNames.settings
    HOME_DIR = os.path.expanduser('~')
    ETC_DIR = '/etc'
    ASSISTANTS_DICT = {'regex': RegexAssistant}
    SUPPORTED_TYPES = {'yaml': YamlConfig}
    DEFAULT_SETTINGS_FACTORY_TYPE = YamlSettingsFactory

    @classmethod
    def load_settings(cls, path):
        with open(path, "r") as config_file:
            whylog_settings = yaml.load(config_file)
            assistant_name = whylog_settings.pop('pattern_assistant')
            assistant_class = cls.ASSISTANTS_DICT.get(assistant_name)
            if assistant_class is None:
                raise UnsupportedAssistantError(assistant_name)
            config_type = whylog_settings.pop('config_type')
            config_class = cls.SUPPORTED_TYPES.get(config_type)
            if config_class is None:
                raise UnsupportedConfigType(config_class)
            return {'config': config_class(**whylog_settings), 'assistant': assistant_class}

    @classmethod
    def get_settings(cls):
        path = cls._find_path_to_settings()
        if path is not None:
            path_to_settings = os.path.join(path, cls.CONFIG_SETTINGS_FILE)
            return cls.load_settings(path_to_settings)
        path_to_settings = cls.DEFAULT_SETTINGS_FACTORY_TYPE.create_new_settings_dir(os.getcwd())
        return cls.load_settings(path_to_settings)

    @classmethod
    def _find_path_to_settings(cls):
        path = cls._search_in_parents_directories(os.getcwd())
        if path is not None:
            return cls._attach_whylog_dir(path)
        dir_to_check = [cls._attach_whylog_dir(cls.HOME_DIR), cls._attach_whylog_dir(cls.ETC_DIR)]
        for directory in dir_to_check:
            if os.path.isdir(directory):
                return directory

    @classmethod
    def _search_in_parents_directories(cls, path):
        if os.path.isdir(cls.WHYLOG_DIR):
            # current directory
            return path
        while True:
            path, suffix = os.path.split(path)
            if suffix == '':
                return None
            if os.path.isdir(cls._attach_whylog_dir(path)):
                return path

    @classmethod
    def _attach_whylog_dir(cls, path):
        return os.path.join(path, cls.WHYLOG_DIR)
