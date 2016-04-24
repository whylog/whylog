from unittest import TestCase

import os
import shutil

from whylog.config import ConfigFactory


class TestBasic(TestCase):
    def test_creating_new_config_dir(self):
        assert ConfigFactory._find_path_to_config() is None
        ConfigFactory.get_config()
        predicted_dir_path = os.path.join(os.getcwd(), ConfigFactory.WHYLOG_DIR)
        assert os.path.isdir(predicted_dir_path)
        assert sorted(os.listdir(predicted_dir_path)) == ['config.yaml', 'log_types.yaml', 'parsers.yaml', 'rules.yaml']
        shutil.rmtree(predicted_dir_path)

    @classmethod
    def find_config_in_parent_dir(cls, path):
        ConfigFactory._create_new_config_dir(path)
        config, _ = ConfigFactory.get_config()
        assert config._parsers_path == os.path.join(path, ConfigFactory.WHYLOG_DIR, 'parsers.yaml')
        shutil.rmtree(os.path.join(path, ConfigFactory.WHYLOG_DIR))

    def test_find_config_in_parent_dir(self):
        path = os.getcwd()
        TestBasic.find_config_in_parent_dir(path)
        for i in range(2):
            path, _ = os.path.split(path)
            TestBasic.find_config_in_parent_dir(path)

    def test_find_config_in_home_directory(self):
        TestBasic.find_config_in_parent_dir(ConfigFactory.HOME_DIR)
