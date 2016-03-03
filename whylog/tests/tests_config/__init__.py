from whylog.teacher import Teacher
from whylog.config import YamlConfig


from unittest import TestCase
from os.path import join

path_test_files = ['whylog', 'tests', 'tests_config', 'test_files']


class TestBasic(TestCase):
    def test_transform(self):
        path = join(*path_test_files)
        parsers_path = join(path, 'parsers.yaml')
        rules_path = join(path, 'rules.yaml')
        input_path = join(path, 'input.txt')
        output_path = join(path, 'expected_output.txt')
        log_location_path = join(path, 'log_locations.yaml')

        config = YamlConfig(parsers_path, rules_path, log_location_path)
        teacher = Teacher(config, [], [])
        teacher.save()
