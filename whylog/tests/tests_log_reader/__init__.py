import os.path
from unittest import TestCase

from generator import generate, generator
from nose.plugins.skip import SkipTest

from whylog.log_reader import LogReader
from whylog.config import YamlConfig
from whylog.tests.tests_log_reader.constants import TestPaths

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
    def test_one(self, test_name):
        prefix_path = os.path.join(*TestPaths.path_test_files)
        path = os.path.join(prefix_path, test_name)
        parsers_path = os.path.join(path, 'parsers.yaml')
        rules_path = os.path.join(path, 'rules.yaml')
        input_path = os.path.join(path, 'input.txt')
        output_path = os.path.join(path, 'expected_output.txt')
        log_location_path = os.path.join(path, 'log_locations.yaml')

        raise SkipTest("Functionality not implemented yet")

        whylog_base = YamlConfig(
            parsers_path=parsers_path,
            rules_path=rules_path,
            log_type_path=log_location_path,
        )

        log_reader = LogReader(config=whylog_base, open_path=path)

        with open(input_path, 'r') as f:
            line = f.read()
        # TODO call get_cause with sens...
        result = log_reader.get_cause(line)

        # TODO check up correctness in appropriate way
        with open(output_path, 'r') as f:
            assert result == f.read()
