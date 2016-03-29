import os
import shutil

import six

from whylog.config import SettingsFactorySelector
from whylog.config.consts import YamlFileNames
from whylog.config.settings_factory import YamlSettingsFactory
from whylog.tests.utils import TestRemovingSettings


class TestBasic(TestRemovingSettings):
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
        YamlSettingsFactory.create_new_settings_dir(
            path, SettingsFactorySelector.WHYLOG_DIR, SettingsFactorySelector.SETTINGS_FILE
        )
        config = SettingsFactorySelector.get_settings()['config']
        expected_path = SettingsFactorySelector._attach_whylog_dir(path)
        cls.validate_created_config(config, expected_path)

    def test_find_config_in_parent_dir(self):
        path = os.getcwd()
        self.find_config_in_parent_dir(path)
        shutil.rmtree(SettingsFactorySelector._attach_whylog_dir(path))
        for i in six.moves.range(2):
            path, _ = os.path.split(path)
            self.find_config_in_parent_dir(path)
            shutil.rmtree(SettingsFactorySelector._attach_whylog_dir(path))

    def test_find_config_in_home_directory(self):
        self.find_config_in_parent_dir(SettingsFactorySelector.HOME_DIR)
        shutil.rmtree(SettingsFactorySelector._attach_whylog_dir(SettingsFactorySelector.HOME_DIR))
