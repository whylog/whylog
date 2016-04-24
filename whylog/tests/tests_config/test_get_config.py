import os
import shutil
from unittest import TestCase

from whylog.config import ConfigFactory


class TestBasic(TestCase):
    @classmethod
    def validate_created_config(cls, config, predicted_dir_path):
        assert os.path.isdir(predicted_dir_path)
        assert config._parsers_path == os.path.join(predicted_dir_path, 'parsers.yaml')
        assert sorted(os.listdir(predicted_dir_path)) == [
            'config.yaml', 'log_types.yaml', 'parsers.yaml', 'rules.yaml'
        ]

    def test_creating_new_config_dir(self):
        assert ConfigFactory._find_path_to_config() is None
        config, _ = ConfigFactory.get_config()
        predicted_dir_path = os.path.join(os.getcwd(), ConfigFactory.WHYLOG_DIR)
        TestBasic.validate_created_config(config, predicted_dir_path)
        shutil.rmtree(predicted_dir_path)

    @classmethod
    def find_config_in_parent_dir(cls, path):
        ConfigFactory._create_new_config_dir(path)
        config, _ = ConfigFactory.get_config()
        expected_path = os.path.join(path, ConfigFactory.WHYLOG_DIR)
        TestBasic.validate_created_config(config, expected_path)
        shutil.rmtree(expected_path)

    def test_find_config_in_parent_dir(self):
        path = os.getcwd()
        TestBasic.find_config_in_parent_dir(path)
        for i in range(2):
            path, _ = os.path.split(path)
            TestBasic.find_config_in_parent_dir(path)

    def test_find_config_in_home_directory(self):
        TestBasic.find_config_in_parent_dir(ConfigFactory.HOME_DIR)

    @classmethod
    def tearDownClass(cls):
        #clean test .whylog directories if some tests fail.
        path = os.getcwd()
        TestBasic.remove_config_dir(path)
        for i in range(2):
            path, _ = os.path.split(path)
            TestBasic.remove_config_dir(path)
        TestBasic.remove_config_dir(ConfigFactory.HOME_DIR)

    @classmethod
    def remove_config_dir(cls, path):
        config_dir = os.path.join(path, ConfigFactory.WHYLOG_DIR)
        if os.path.isdir(config_dir):
            shutil.rmtree(config_dir)
