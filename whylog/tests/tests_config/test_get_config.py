import os
import shutil
from unittest import TestCase

from whylog.config import ConfigFactory


class TestBasic(TestCase):
    @classmethod
    def setUpClass(cls):
        #This change was caused by fails os.names() for new directories.
        #Renaming was necessary to avoid conflicts between test config directories
        #and orginal independent non tests config directories
        ConfigFactory.WHYLOG_DIR = '.whylog_test'

    @classmethod
    def validate_created_config(cls, config, predicted_dir_path):
        assert os.path.isdir(predicted_dir_path)
        assert config._parsers_path == os.path.join(predicted_dir_path, 'parsers.yaml')
        assert sorted(os.listdir(predicted_dir_path)) == [
            'config.yaml', 'log_types.yaml', 'parsers.yaml', 'rules.yaml'
        ]

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
        #Removed test config directories if test failed
        path = os.getcwd()
        TestBasic.remove_config_dir(path)
        for i in range(2):
            path, _ = os.path.split(path)
            TestBasic.remove_config_dir(path)
        TestBasic.remove_config_dir(ConfigFactory.HOME_DIR)
        ConfigFactory.WHYLOG_DIR = '.whylog'

    @classmethod
    def remove_config_dir(cls, path):
        config_dir = os.path.join(path, ConfigFactory.WHYLOG_DIR)
        if os.path.isdir(config_dir):
            shutil.rmtree(config_dir)
