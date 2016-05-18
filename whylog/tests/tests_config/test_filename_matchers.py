import os.path
import shutil
from datetime import datetime
from unittest import TestCase

from whylog.config import SettingsFactorySelector
from whylog.config.filename_matchers import WildCardFilenameMatcher
from whylog.config.log_type import LogType
from whylog.config.super_parser import RegexSuperParser
from whylog.tests.utils import TestPaths

path_test_files = ['whylog', 'tests', 'tests_config', 'test_files', 'simple_logs_files']


class TestBasic(TestCase):
    def test_parsed_distinct_files(self):
        path = os.path.join(*path_test_files)
        suffix_1 = 'node_1.log'
        suffix_2 = 'node_[12].log'
        super_parser = RegexSuperParser('^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d).*', [1], {1: 'date'})
        matcher_1 = WildCardFilenameMatcher(
            'localhost', os.path.join(path, suffix_1), 'default', super_parser
        )
        matcher_2 = WildCardFilenameMatcher(
            'localhost', os.path.join(path, suffix_2), 'default', super_parser
        )
        log_type = LogType('default', [matcher_1, matcher_2])

        assert sorted(log_type.files_to_parse()) == [
            ('localhost', os.path.join(path, 'node_1.log'), super_parser),
            ('localhost', os.path.join(path, 'node_2.log'), super_parser)
        ]

    def test_add_log_type(self):
        SettingsFactorySelector.WHYLOG_DIR = TestPaths.WHYLOG_DIR
        config = SettingsFactorySelector.get_settings()['config']
        whylog_dir = SettingsFactorySelector._attach_whylog_dir(os.getcwd())

        super_parser = RegexSuperParser('^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d).*', [1], {1: 'date'})
        matcher = WildCardFilenameMatcher('localhost', 'node_1.log', 'default', super_parser)
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
        assert matcher.super_parser == super_parser
        assert isinstance(matcher, WildCardFilenameMatcher)

        shutil.rmtree(whylog_dir)

    def test_super_parser(self):
        line = '2015-12-03 12:08:09 Connection error occurred on alfa36. Host name: 2'

        super_parser1 = RegexSuperParser('^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d).*', [1], {1: 'date'})
        assert super_parser1.get_ordered_groups(line) == [('date', datetime(2015, 12, 3, 12, 8, 9))]

        super_parser2 = RegexSuperParser(
            '^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d).* Host name: (\d+)', [2, 1], {
                1: 'date',
                2: 'int'
            }
        )
        assert super_parser2.get_ordered_groups(line) == [
            ('int', 2), ('date', datetime(2015, 12, 3, 12, 8, 9))
        ]

        super_parser3 = RegexSuperParser('foo bar', [], {})
        assert super_parser3.get_ordered_groups(line) == tuple()

    @classmethod
    def tearDownClass(cls):
        whylog_dir = SettingsFactorySelector._attach_whylog_dir(os.getcwd())
        if os.path.isdir(whylog_dir):
            shutil.rmtree(whylog_dir)
