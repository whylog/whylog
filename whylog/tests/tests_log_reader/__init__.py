import os.path
from unittest import TestCase

from generator import generate, generator
from nose.plugins.skip import SkipTest

from whylog.config import YamlConfig
from whylog.log_reader import LogReader
from whylog.tests.tests_log_reader.constants import TestPaths
from whylog.front import FrontInput

path_test_files = ['whylog', 'tests', 'tests_log_reader', 'test_files']


@generator
class TestBasic(TestCase):
    def _line_offset(self, file_path):
        return 42

    def _get_last_line_from_file(self, file_path):
        return [line.rstrip('\n') for line in open(file_path)][-1]

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
        log_type_path = os.path.join(path, 'log_types.yaml')
        log_file = os.path.join(path, 'node_1.log')

        if not test_name == '003_match_time_range':
            # TODO this 'if' is temporary, remove this later
            raise SkipTest("Functionality not implemented yet")

        whylog_config = YamlConfig(
            parsers_path=parsers_path,
            rules_path=rules_path,
            log_type_path=log_type_path,
        )

        log_reader = LogReader(whylog_config)

        with open(output_path, 'r') as f:
            f.readline()
            line_content = f.readline()
            # ^ hack basing on that effect-line is in 2nd line in each expected_output.txt file

        line = FrontInput(
            self._line_offset(log_file), line_content, prefix_path)  # TODO how to get right offset?
        result = log_reader.get_causes(line)

        if test_name == '003_match_time_range':
            # TODO this 'if' is temporary, remove this later
            assert result.line_content == self._get_last_line_from_file(output_path)
            # ^ hack basing on that for test 003 last line of expected_output.txt is a cause line
            # FIXME it is not appropriate for each test
            # FIXME checking up correctness should be more advanced for more advanced tests
