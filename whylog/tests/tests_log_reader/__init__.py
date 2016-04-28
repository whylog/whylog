import os.path
from unittest import TestCase
import platform

from generator import generate, generator
from nose.plugins.skip import SkipTest

from whylog.config import YamlConfig
from whylog.front import FrontInput
from whylog.log_reader import LogReader
from whylog.tests.tests_log_reader.constants import TestPaths
from whylog.tests.utils import ConfigPathFactory

path_test_files = ['whylog', 'tests', 'tests_log_reader', 'test_files']


@generator
class TestBasic(TestCase):
    def _get_cause_line_number(self, file_path):
        """
        returns number of line that should be used as get_causes input
        according to information contained in 'input.txt' file
        """
        # it is reduced by 1 because auxiliary functions below use numerating from 0
        return int(open(file_path).readline().split(":")[1].rstrip('\n')) - 1

    def _get_concrete_line_from_file(self, file_path, line_num):
        return [line.rstrip('\n') for line in open(file_path)][line_num]

    def _deduce_line_offset(self, file_path, line_no):
        """ returns offset of line 'line_no' in file 'file_path' """
        return sum([len(line) for line in open(file_path)][0:line_no])

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
        input_path = os.path.join(path, 'input.txt')
        output_path = os.path.join(path, 'expected_output.txt')
        log_file = os.path.join(path, 'node_1.log')
        log_type_path = os.path.join(path, 'log_types.yaml')

        # TODO this 'if' is temporary, remove this later
        if not test_name == '003_match_time_range':
            raise SkipTest("Functionality not implemented yet")

        if platform.system() == 'Windows':
            log_type_path = log_type_path.replace('/', '\\')

        line_number = self._get_cause_line_number(input_path)
        line_content = self._get_concrete_line_from_file(log_file, line_number)
        effect_line_offset = self._deduce_line_offset(log_file, line_number)

        whylog_config = YamlConfig(*ConfigPathFactory.get_path_to_config_files(path))
        log_reader = LogReader(whylog_config)
        line = FrontInput(effect_line_offset, line_content, prefix_path)

        result = log_reader.get_causes(line)

        if test_name == '003_match_time_range':
            # TODO this 'if' is temporary, remove this later
            assert result
            assert result[0].line_content == self._get_last_line_from_file(output_path)
            # ^ hack basing on that for test 003 last line of expected_output.txt is a cause line
            # FIXME it is not appropriate for each test
            # FIXME checking up correctness should be more advanced for more advanced tests
