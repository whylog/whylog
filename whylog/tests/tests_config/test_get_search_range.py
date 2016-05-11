import shutil
import os.path
from datetime import datetime
from unittest import TestCase

from whylog.config.investigation_plan import Clue, LineSource
from whylog.config.parsers import RegexParser
from whylog.config.rule import Rule
from whylog.config import SettingsFactorySelector
from whylog.tests.consts import TestPaths


class TestBasic(TestCase):
    @classmethod
    def setUpClass(cls):
        SettingsFactorySelector.WHYLOG_DIR = TestPaths.WHYLOG_DIR
        cls.config = SettingsFactorySelector.get_settings()['config']
        cls.whylog_dir = SettingsFactorySelector._attach_whylog_dir(os.getcwd())

        cause1_regex = '^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) cause1 transaction number: (\d+) Host: (\w)$'
        cause1_line = '2016-04-12 23:39:43 cause1 transaction number: 10101 Host: db_host'
        convertions = {1: 'date'}
        cause1 = RegexParser(
            "cause1", cause1_line, cause1_regex, [1], 'database', convertions
        )

        cause2_regex = '^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) cause2 moved resource id: (\d+) Host: (\w)$'
        cause2_line = '2016-04-12 23:40:43 cause2 moved resource id: 1234 Host: apache_host'
        convertions = {1: 'date'}
        cause2 = RegexParser(
            "cause2", cause2_line, cause2_regex, [1], 'apache', convertions
        )

        effect_regex = '^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) effect internal server error Host: (\w)$'
        effect_line = '2016-04-12 23:54:43 effect internal server error Host: apache_host'
        convertions = {1: 'date'}
        effect = RegexParser(
            "effect", effect_line, effect_regex, [1], 'apache', convertions
        )

        constraints = [
            {
                'clues_groups': [[1, 1], [0, 1]],
                'name': 'time',
                'params': {'max_delta': 100, 'min_delta': 10}
            },
            {
                'clues_groups': [[2, 1], [0, 1]],
                'name': 'time',
                'params': {'max_delta': 10}
            }
        ]

        cls.rule = Rule([cause1, cause2], effect, constraints)
        cls.config._rules['apache'] = cls.rule

    def test_get_search_range(self):
        line_source = LineSource('localhost', 'node_1.log')
        effect_time = datetime(2016, 4, 12, 23, 54, 43)
        effect_line = '2016-04-12 23:54:43 effect internal server error Host: apache_host'
        effect_clues = {'effect': Clue((effect_time,), effect_line, 40, line_source)}

        calculated_ranges = self.config._get_search_ranges([self.rule], effect_clues)

        expected_ranges = {'database': {'date': {'max': datetime(2016, 4, 12, 23, 53, 3),
                                                 'min': datetime(2016, 4, 12, 23, 54, 33)}},
                           'apache': {'date': {'max': datetime(2016, 4, 12, 23, 54, 33)}}}

        assert calculated_ranges == expected_ranges

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.whylog_dir)
