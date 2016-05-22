import os.path
import shutil
from datetime import datetime
from unittest import TestCase

from whylog.config import SettingsFactorySelector
from whylog.config.investigation_plan import Clue, LineSource
from whylog.config.parsers import RegexParser
from whylog.config.rule import Rule
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
        cls.cause1 = RegexParser("cause1", cause1_line, cause1_regex, [1], 'database', convertions)

        cause2_regex = '^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) cause2 moved resource id: (\d+) Host: (\w)$'
        cause2_line = '2016-04-12 23:40:43 cause2 moved resource id: 1234 Host: apache_host'
        convertions = {1: 'date'}
        cls.cause2 = RegexParser("cause2", cause2_line, cause2_regex, [1], 'apache', convertions)

        effect_regex = '^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) effect internal server error Host: (\w)$'
        effect_line = '2016-04-12 23:54:43 effect internal server error Host: apache_host'
        convertions = {1: 'date'}
        cls.effect = RegexParser("effect", effect_line, effect_regex, [1], 'apache', convertions)

        line_source = LineSource('localhost', 'node_1.log')
        cls.effect_time = datetime(2016, 4, 12, 23, 54, 43)
        effect_line = '2016-04-12 23:54:43 effect internal server error Host: apache_host'
        cls.effect_clues = {
            'effect': Clue(
                (cls.effect_time, 'apache_host'), effect_line, 40, line_source)
        }

        cls.earliest_date = datetime.min
        cls.ten_second_earlier = datetime(2016, 4, 12, 23, 54, 33)
        cls.one_hundred_second_earlier = datetime(2016, 4, 12, 23, 53, 3)
        cls.ten_second_later = datetime(2016, 4, 12, 23, 54, 53)

    @classmethod
    def calculate_range(cls, rules):
        cls.config._rules['apache'].extend(rules)
        calculated_ranges = cls.config._get_search_ranges(rules, cls.effect_clues)
        cls.config._rules['apache'].pop()
        return calculated_ranges

    def test_search_range_no_constraints_on_primary_values(self):
        rule = Rule([self.cause1, self.cause2], self.effect, [], Rule.LINKAGE_AND)
        calculated_ranges = self.calculate_range([rule])

        expected_ranges = {
            'apache': {
                'date': {
                    'left_bound': self.earliest_date,
                    'right_bound': self.effect_time
                }
            },
            'database': {
                'date': {
                    'left_bound': self.earliest_date,
                    'right_bound': self.effect_time
                }
            }
        } # yapf: disable

        assert calculated_ranges == expected_ranges

    def test_search_range_single_log_types(self):
        constraints = [
            {
                'clues_groups': [[1, 1], [0, 1]],
                'name': 'time',
                'params': {'max_delta': 10}
            }
        ]  # yapf: disable
        rule = Rule([self.cause2], self.effect, constraints, Rule.LINKAGE_AND)
        calculated_ranges = self.calculate_range([rule])

        expected_ranges = {
            'apache': {
                'date': {
                    'left_bound': self.ten_second_earlier,
                    'right_bound': self.effect_time
                }
            }
        }  # yapf: disable

        assert calculated_ranges == expected_ranges

    def test_search_range_two_log_types(self):
        constraints1 = [
            {
                'clues_groups': [[1, 1], [0, 1]],
                'name': 'time',
                'params': {
                    'max_delta': 100,
                    'min_delta': 10
                }
            }, {
                'clues_groups': [[2, 1], [0, 1]],
                'name': 'time',
                'params': {'max_delta': 10}
            }
        ]  # yapf: disable
        rule = Rule([self.cause1, self.cause2], self.effect, constraints1, Rule.LINKAGE_AND)
        calculated_ranges = self.calculate_range([rule])

        expected_ranges = {
            'database': {
                'date': {
                    'left_bound': self.one_hundred_second_earlier,
                    'right_bound': self.ten_second_earlier
                }
            },
            'apache': {
                'date': {
                    'left_bound': self.ten_second_earlier,
                    'right_bound': self.effect_time
                }
            }
        }  # yapf: disable

        assert calculated_ranges == expected_ranges

    def test_search_range_lack_of_left_bound(self):
        constraints1 = [
            {
                'clues_groups': [[1, 1], [0, 1]],
                'name': 'time',
                'params': {'min_delta': 10}
            },
        ]  # yapf: disable
        rule = Rule([self.cause1], self.effect, constraints1, Rule.LINKAGE_AND)
        calculated_ranges = self.calculate_range([rule])

        expected_ranges = {
            'database': {
                'date': {
                    'left_bound': self.earliest_date,
                    'right_bound': self.ten_second_earlier
                }
            },
        }  # yapf: disable

        assert calculated_ranges == expected_ranges

    def test_search_range_lack_of_right_bound(self):
        constraints1 = [
            {
                'clues_groups': [[1, 1], [0, 1]],
                'name': 'time',
                'params': {'max_delta': 10}
            },
        ]  # yapf: disable
        rule = Rule([self.cause1], self.effect, constraints1, Rule.LINKAGE_AND)
        calculated_ranges = self.calculate_range([rule])

        expected_ranges = {
            'database': {
                'date': {
                    'left_bound': self.ten_second_earlier,
                    'right_bound': self.effect_time
                }
            },
        }  # yapf: disable

        assert calculated_ranges == expected_ranges

    def test_search_range_delayed_logs(self):
        constraints1 = [
            {
                'clues_groups': [[1, 1], [0, 1]],
                'name': 'time',
                'params': {
                    'min_delta': -10,
                    'max_delta': 100
                }
            },
        ]  # yapf: disable
        rule = Rule([self.cause1], self.effect, constraints1, Rule.LINKAGE_AND)
        calculated_ranges = self.calculate_range([rule])

        expected_ranges = {
            'database': {
                'date': {
                    'left_bound': self.one_hundred_second_earlier,
                    'right_bound': self.ten_second_later
                }
            },
        }  # yapf: disable

        assert calculated_ranges == expected_ranges

    def test_search_range_merge_range(self):
        constraints1 = [
            {
                'clues_groups': [[1, 1], [0, 1]],
                'name': 'time',
                'params': {
                    'max_delta': 75,
                    'min_delta': 10
                }
            }, {
                'clues_groups': [[2, 1], [0, 1]],
                'name': 'time',
                'params': {'max_delta': 10}
            }, {
                'clues_groups': [[3, 1], [0, 1]],
                'name': 'time',
                'params': {
                    'max_delta': 100,
                    'min_delta': 20
                }
            }, {
                'clues_groups': [[4, 1], [0, 1]],
                'name': 'time',
                'params': {
                    'max_delta': 100,
                    'min_delta': 20
                }
            }
        ]  # yapf: disable
        rule = Rule(
            [
                self.cause1, self.cause2, self.cause1, self.cause2
            ], self.effect, constraints1, Rule.LINKAGE_AND
        )
        calculated_ranges = self.calculate_range([rule])

        expected_ranges = {
            'database': {
                'date': {
                    'left_bound': self.one_hundred_second_earlier,
                    'right_bound': self.ten_second_earlier
                }
            },
            'apache': {
                'date': {
                    'left_bound': self.one_hundred_second_earlier,
                    'right_bound': self.effect_time
                }
            }
        }  # yapf: disable

        assert calculated_ranges == expected_ranges

    def test_search_range_covering(self):
        constraints1 = [
            {
                'clues_groups': [[1, 1], [0, 1]],
                'name': 'time',
                'params': {
                    'max_delta': 75,
                    'min_delta': 10
                }
            },
            {
                'clues_groups': [[2, 1], [0, 1]],
                'name': 'time',
                'params': {'max_delta': 100}
            },
        ]  # yapf: disable
        rule = Rule([self.cause2, self.cause2], self.effect, constraints1, Rule.LINKAGE_AND)
        calculated_ranges = self.calculate_range([rule])

        expected_ranges = {
            'apache': {
                'date': {
                    'left_bound': self.one_hundred_second_earlier,
                    'right_bound': self.effect_time
                }
            }
        }  # yapf: disable

        assert calculated_ranges == expected_ranges

    def test_search_range_reasoning_on_not_only_effect(self):
        constraints1 = [
            {
                'clues_groups': [[1, 1], [0, 1]],
                'name': 'time',
                'params': {
                    'max_delta': 75,
                    'min_delta': 10
                }
            },
            {
                'clues_groups': [[2, 1], [1, 1]],
                'name': 'time',
                'params': {'max_delta': 25}
            },
        ]  # yapf: disable
        rule = Rule([self.cause2, self.cause2], self.effect, constraints1, Rule.LINKAGE_AND)
        calculated_ranges = self.calculate_range([rule])

        expected_ranges = {
            'apache': {
                'date': {
                    'left_bound': self.one_hundred_second_earlier,
                    'right_bound': self.ten_second_earlier
                }
            }
        }  # yapf: disable

        assert calculated_ranges == expected_ranges

    def test_search_range_mixed_constraint_type(self):
        constraints1 = [
            {
                'clues_groups': [[1, 1], [0, 1]],
                'name': 'time',
                'params': {
                    'max_delta': 100,
                    'min_delta': 10
                }
            },
            {
                'clues_groups': [[2, 3], [0, 2]],
                'name': 'identical',
                'params': {}
            },
        ] # yapf: disable
        rule = Rule([self.cause2, self.cause2], self.effect, constraints1, Rule.LINKAGE_AND)
        calculated_ranges = self.calculate_range([rule])

        expected_ranges = {
            'apache': {
                'date': {
                    'left_bound': self.earliest_date,
                    'right_bound': self.effect_time
                }
            }
        } # yapf: disable

        assert calculated_ranges == expected_ranges

    def test_search_range_two_constraints_on_one_group(self):
        constraints1 = [
            {
                'clues_groups': [[1, 1], [0, 1]],
                'name': 'time',
                'params': {
                    'max_delta': 100,
                    'min_delta': 10
                }
            },
            {
                'clues_groups': [[2, 1], [0, 1]],
                'name': 'time',
                'params': {
                    'max_delta': 100,
                }
            },
            {
                'clues_groups': [[2, 3], [0, 2]],
                'name': 'identical',
                'params': {}
            },
        ] # yapf: disable
        rule = Rule([self.cause2, self.cause2], self.effect, constraints1, Rule.LINKAGE_AND)
        calculated_ranges = self.calculate_range([rule])

        expected_ranges = {
            'apache': {
                'date': {
                    'left_bound': self.one_hundred_second_earlier,
                    'right_bound': self.effect_time
                }
            }
        } # yapf: disable

        assert calculated_ranges == expected_ranges

        rule = Rule([self.cause2, self.cause2], self.effect, constraints1, Rule.LINKAGE_OR)
        calculated_ranges = self.calculate_range([rule])

        expected_ranges = {
            'apache': {
                'date': {
                    'left_bound': self.earliest_date,
                    'right_bound': self.effect_time
                }
            }
        } # yapf: disable

        assert calculated_ranges == expected_ranges

    def test_search_range_multiple_rules(self):
        constraints1 = [
            {
                'clues_groups': [[1, 1], [0, 1]],
                'name': 'time',
                'params': {'max_delta': 10}
            }
        ] # yapf: disable
        rule1 = Rule([self.cause2], self.effect, constraints1, Rule.LINKAGE_AND)
        constraints2 = [
            {
                'clues_groups': [[1, 1], [0, 1]],
                'name': 'time',
                'params': {
                    'max_delta': 100,
                    'min_delta': 10
                }
            }, {
                'clues_groups': [[2, 1], [0, 1]],
                'name': 'time',
                'params': {'max_delta': 100}
            }
        ] # yapf: disable
        rule2 = Rule([self.cause1, self.cause2], self.effect, constraints2, Rule.LINKAGE_AND)
        calculated_ranges = self.calculate_range([rule1, rule2])

        expected_ranges = {
            'database': {
                'date': {
                    'left_bound': self.one_hundred_second_earlier,
                    'right_bound': self.ten_second_earlier
                }
            },
            'apache': {
                'date': {
                    'left_bound': self.one_hundred_second_earlier,
                    'right_bound': self.effect_time
                }
            }
        } # yapf: disable

        assert calculated_ranges == expected_ranges

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.whylog_dir)
