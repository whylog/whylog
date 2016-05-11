import shutil
import os.path
from unittest import TestCase

from whylog.config import SettingsFactorySelector
from whylog.config.filename_matchers import WildCardFilenameMatcher
from whylog.config.log_type import LogType
from whylog.tests.utils import TestPaths

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

    def test_add_log_type(self):
        SettingsFactorySelector.WHYLOG_DIR = TestPaths.WHYLOG_DIR
        config = SettingsFactorySelector.get_settings()['config']
        whylog_dir = SettingsFactorySelector._attach_whylog_dir(os.getcwd())

        matcher = WildCardFilenameMatcher('localhost', 'node_1.log', 'default')
        default_log_type = LogType('default', [matcher])
        config.add_log_type(default_log_type)

        config = SettingsFactorySelector.get_settings()['config']
        assert len(config._log_types) == 1
        log_type = config._log_types['default']
        assert log_type.name == 'default'
        assert len(log_type.filename_matchers) == 1
        matcher = log_type.filename_matchers[0]
        assert matcher.host_pattern == 'localhost'
        assert matcher.path_pattern == 'node_1.log'
        assert matcher.log_type_name == 'default'
        assert isinstance(matcher, WildCardFilenameMatcher)

        shutil.rmtree(whylog_dir)

    @classmethod
    def tearDownClass(cls):
        whylog_dir = SettingsFactorySelector._attach_whylog_dir(os.getcwd())
        if os.path.isdir(whylog_dir):
            shutil.rmtree(whylog_dir)
