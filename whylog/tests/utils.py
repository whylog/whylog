import os
import platform

import shutil
from unittest import TestCase

from whylog.config import SettingsFactorySelector
from whylog.config.consts import YamlFileNames
from whylog.tests.consts import TestPaths


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


class TestRemovingSettings(TestCase):
    @classmethod
    def setUpClass(cls):
        #This change was caused by fails os.names() for new directories.
        #Renaming was necessary to avoid conflicts between test config directories
        #and orginal independent non tests config directories
        SettingsFactorySelector.WHYLOG_DIR = TestPaths.WHYLOG_DIR
        cls.remove_settings_dirs()

    @classmethod
    def tearDownClass(cls):
        #Removed test config directories if test failed
        cls.remove_settings_dirs()

    @classmethod
    def remove_one_settings_dir(clas, path):
        config_dir = os.path.join(path, SettingsFactorySelector.WHYLOG_DIR)
        if os.path.isdir(config_dir):
            shutil.rmtree(config_dir)

    @classmethod
    def remove_settings_dirs(cls):
        current_path = os.getcwd()
        cls.remove_one_settings_dir(current_path)
        for i in range(2):
            current_path, _ = os.path.split(current_path)
            cls.remove_one_settings_dir(current_path)
        cls.remove_one_settings_dir(SettingsFactorySelector.HOME_DIR)
