import os.path

from unittest import TestCase

from whylog.config.filename_matchers import WildCardFilenameMatcher
from whylog.config.log_type import LogType

path_test_files = ['whylog', 'tests', 'tests_config', 'test_files', 'simple_logs_files']


class TestBasic(TestCase):
    def test_parsed_distinct_files(self):
        path = os.path.join(*path_test_files)
        suffix_1 = 'node_1.log'
        suffix_2 = 'node_[12].log'
        matcher_1 = WildCardFilenameMatcher('localhost', os.path.join(path, suffix_1), 'default')
        matcher_2 = WildCardFilenameMatcher('localhost', os.path.join(path, suffix_2), 'default')
        log_type = LogType('default', [matcher_1, matcher_2])

        assert sorted(log_type.files_to_parse()) == [
            ('localhost', os.path.join(path, 'node_1.log')),
            ('localhost', os.path.join(path, 'node_2.log'))
        ]
