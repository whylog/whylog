import os.path
from unittest import TestCase
import shutil


from whylog.config import SettingsFactorySelector
from whylog.config.filename_matchers import WildCardFilenameMatcher
from whylog.config.log_type import LogType
from whylog.config.super_parser import RegexSuperParser
from whylog.tests.consts import TestPaths


class TestLogTypeRename(TestCase):
    @classmethod
    def setUpClass(cls):
        SettingsFactorySelector.WHYLOG_DIR = TestPaths.WHYLOG_DIR

    def test_simple_log_type_rename(self):
        config = SettingsFactorySelector.get_settings()['config']
        # rule = Rule(
        #     [self.cause_a], self.effect, [
        #         {
        #             'clues_groups': [[0, 1], [1, 1]],
        #             'name': 'identical',
        #             'params': {}
        #         }
        #     ], Rule.LINKAGE_NOT
        # )
        # super_parser = RegexSuperParser('^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d).*', [1], {1: 'date'})
        # log_type = LogType()

    @classmethod
    def tearDownClass(cls):
        # remove .test_directory if
        test_whylog_dir = SettingsFactorySelector._attach_whylog_dir(os.getcwd())
        if os.path.isdir(test_whylog_dir):
            shutil.rmtree(test_whylog_dir)
