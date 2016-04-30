import os
import shutil
from unittest import TestCase

from whylog.config import SettingsFactorySelector, YamlSettingsFactory
from whylog.config.consts import YamlFileNames
from whylog.tests.consts import TestPaths


class TestBasic(TestCase):
    @classmethod
    def setUpClass(cls):
        #This change was caused by fails os.names() for new directories.
        #Renaming was necessary to avoid conflicts between test config directories
        #and orginal independent non tests config directories
        SettingsFactorySelector.WHYLOG_DIR = TestPaths.WHYLOG_DIR

    @classmethod
    def validate_created_config(cls, config, predicted_dir_path):
        assert os.path.isdir(predicted_dir_path)
        assert config._parsers_path == os.path.join(predicted_dir_path, YamlFileNames.parsers)
        assert sorted(os.listdir(predicted_dir_path)) == [
            YamlFileNames.default_log_types,
            YamlFileNames.parsers,
            YamlFileNames.rules,
            YamlFileNames.settings,
        ]

    @classmethod
    def find_config_in_parent_dir(cls, path):
        YamlSettingsFactory.create_new_settings_dir(path)
        config = SettingsFactorySelector.get_settings()['config']
        expected_path = SettingsFactorySelector._attach_whylog_dir(path)
        cls.validate_created_config(config, expected_path)

    def test_find_config_in_parent_dir(self):
        path = os.getcwd()
        self.find_config_in_parent_dir(path)
        shutil.rmtree(SettingsFactorySelector._attach_whylog_dir(path))
        for i in range(2):
            path, _ = os.path.split(path)
            self.find_config_in_parent_dir(path)
            shutil.rmtree(SettingsFactorySelector._attach_whylog_dir(path))

    def test_find_config_in_home_directory(self):
        self.find_config_in_parent_dir(SettingsFactorySelector.HOME_DIR)
        shutil.rmtree(SettingsFactorySelector._attach_whylog_dir(SettingsFactorySelector.HOME_DIR))

    @classmethod
    def tearDownClass(cls):
        #Removed test config directories if test failed
        path = os.getcwd()
        cls.remove_config_dir(path)
        for i in range(2):
            path, _ = os.path.split(path)
            cls.remove_config_dir(path)
        cls.remove_config_dir(SettingsFactorySelector.HOME_DIR)

    @classmethod
    def remove_config_dir(cls, path):
        config_dir = os.path.join(path, SettingsFactorySelector.WHYLOG_DIR)
        if os.path.isdir(config_dir):
            shutil.rmtree(config_dir)
