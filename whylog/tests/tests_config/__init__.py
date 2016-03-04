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

        config = YamlConfig(parsers_path, rules_path, None)
        teacher = Teacher(config, [], [])
        teacher.save()
