from unittest import TestCase
import os.path

from generator import generator, generate
from nose.plugins.skip import SkipTest

from whylog.tests.tests_client.constants import TestPaths
from whylog.config import YamlConfig
from whylog.client import WhylogClient

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
        prefix_path = os.path.join(*TestPaths.path_test_files)
        path = os.path.join(prefix_path, test_name)
        parsers_path = os.path.join(path, 'parsers.yaml')
        rules_path = os.path.join(path, 'rules.yaml')
        input_path = os.path.join(path, 'input.txt')
        output_path = os.path.join(path, 'expected_output.txt')
        log_location_path = os.path.join(path, 'log_locations.yaml')

        whylog_base = YamlConfig(
            parsers_path=parsers_path,
            rules_path=rules_path,
            log_locations_path=log_location_path,
        )
        raise SkipTest("Functionality not implemented yet")
        whylog_client = WhylogClient(config=whylog_base, open_path=path)

        with open(input_path, 'r') as f:
            vim_line = f.read()
        # TODO call get_cause with sens...
        result = whylog_client.get_cause(1, vim_line)

        # TODO check up correctness in appropriate way
        with open(output_path, 'r') as f:
            assert result == f.read()
