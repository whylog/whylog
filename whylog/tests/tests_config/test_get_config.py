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
