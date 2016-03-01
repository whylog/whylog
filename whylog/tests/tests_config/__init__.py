from unittest import TestCase
from os.path import join

from whylog.config import YamlConfig

path_test_files = ['whylog', 'tests', 'tests_config', 'test_files']


class TestConfig(TestCase):
    def test_file_loading(self):
        path = join(*path_test_files)
        parsers_path = join(path, 'parsers.yaml')
        rules_path = join(path, 'rules.yaml')
        log_location_path = join(path, 'log_locations.yaml')

        config = YamlConfig(
            parsers_path=parsers_path,
            rules_path=rules_path,
            log_locations_path=log_location_path,
        )