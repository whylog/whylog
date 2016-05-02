import os

import yaml

from whylog.assistant.exceptions import UnsupportedAssistantError
from whylog.assistant.regex_assistant import RegexAssistant
from whylog.config.consts import YamlFileNames
from whylog.config.exceptions import UnsupportedConfigType
from whylog.config.settings_factory import YamlSettingsFactory
from whylog.config.yaml_config import YamlConfig


class SettingsFactorySelector(object):
    """
    This class is responsible for finding .whylog directory (whylog settings directory) and basing on
    found content directory creating settings. If not found then it creates minimal
    .whylog version in current directory.
    """
    WHYLOG_DIR = '.whylog'
    SETTINGS_FILE = YamlFileNames.settings
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
            path_to_settings = os.path.join(path, cls.SETTINGS_FILE)
            return cls.load_settings(path_to_settings)
        path_to_settings = cls.DEFAULT_SETTINGS_FACTORY_TYPE.create_new_settings_dir(
            os.getcwd(), cls.WHYLOG_DIR, cls.SETTINGS_FILE
        )
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
