from os.path import join as path_join
from unittest import TestCase

from generator import generate, generator
from nose.plugins.skip import SkipTest

from whylog.client import WhylogClient
from whylog.config import YamlConfig

path_test_files = ['whylog', 'tests', 'tests_client', 'test_files']


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
    def test_one(self, test_name):
        prefix_path = path_join(*path_test_files)
        path = path_join(prefix_path, test_name)
        parsers_path = path_join(path, 'parsers.yaml')
        rules_path = path_join(path, 'rules.yaml')
        input_path = path_join(path, 'input.txt')
        output_path = path_join(path, 'expected_output.txt')
        log_location_path = path_join(path, 'log_locations.yaml')

        whylog_base = YamlConfig(
            parsers_path=parsers_path,
            rules_path=rules_path,
            log_locations_path=log_location_path,
        )
        whylog_client = WhylogClient(base=whylog_base, open_path=path)

        with open(input_path, 'r') as f:
            vim_line = f.read()
        result = whylog_client.get_cause(vim_line)

        raise SkipTest('Not implemented yet')
        with open(output_path, 'r') as f:
            pass
            # remove this comment after implement whylog client and base
            # assert result == f.read()

    def test_imports_correctness(self):
        client = WhylogClient()
