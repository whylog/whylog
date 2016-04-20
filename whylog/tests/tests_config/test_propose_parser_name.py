from __future__ import print_function
import os.path
from unittest import TestCase


from whylog.config import YamlConfig

path_test_files = ['whylog', 'tests', 'tests_config', 'test_files']


class TestBasic(TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.path.join(*path_test_files)
        parsers_path = os.path.join(path, 'parsers.yaml')
        rules_path = os.path.join(path, 'rules.yaml')
        log_type_path = os.path.join(path, 'log_types.yaml')

        cls.sample_line1 = "2016-04-12 23:54:45 Connection error occurred on comp1. Host name: host1"

        cls.config = YamlConfig(parsers_path, rules_path, log_type_path)

    def test_is_free_parser_name(self):
        assert not self.config.is_free_parser_name('lostdata')
        assert not self.config.is_free_parser_name('connectionerror')
        assert not self.config.is_free_parser_name('datamigration')

