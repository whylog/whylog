import os.path
from unittest import TestCase

from generator import generate, generator


from whylog.config.filename_matchers import WildCardFilenameMatcher

path_test_files = ['whylog', 'tests', 'tests_log_reader', 'test_files']


@generator
class TestBasic(TestCase):
    @generate(
        '001_most_basic',
        '002_match_latest',
        '003_match_time_range',
        '005_match_tree',
        '006_match_parameter',
        '007_match_or',
        '008_match_and',
        '009_match_negation',
        '010_multiple_files',
        '011_different_entry',
        '012_multiple_rulebooks',
        '013_match_and_incomplete',
    )
    def test_filename_matchers(self, test_name):
        prefix_path = os.path.join(*path_test_files)
        path = os.path.join(prefix_path, test_name)
        matcher = WildCardFilenameMatcher('localhost', os.path.join(path, 'node_[123].log'), 'default')
        print len(matcher.get_matched_files())

    # def test_simple_wildcard_matcher(self):
