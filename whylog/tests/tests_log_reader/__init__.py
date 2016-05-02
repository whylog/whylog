import os.path
from unittest import TestCase

from generator import generate, generator

from whylog.config import YamlConfig
from whylog.config.investigation_plan import LineSource
from whylog.constraints.verifier import InvestigationResult
from whylog.front.utils import FrontInput
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

    def _deduce_line_offset_by_unique_content(self, file_path, line_content):
        all_lines = [line.rstrip('\n') for line in open(file_path)]
        line_no = all_lines.index(line_content)
        return self._deduce_line_offset(file_path, line_no)

    def _get_last_line_from_file(self, file_path):
        return [line.rstrip('\n') for line in open(file_path)][-1]

    def _investigation_results_from_file(self, log_file, file_path):
        results = []
        file_content = [line.rstrip('\n') for line in open(file_path)]
        for (linkage, lines_str, constraint_str) in zip(
            *[
                [
                    x for (i, x) in enumerate(file_content) if (i % 3 == num)
                ] for num in range(3)
            ]
        ):
            # TODO enable upgrading InvRes with linkage (AND,OR,NOT) when support for linkage will be merged
            lines = [
                FrontInput(
                    self._deduce_line_offset_by_unique_content(log_file, line_str), line_str,
                    LineSource("localhost", "node_1.log")
                ) for line_str in eval(lines_str)
            ]
            results.append(InvestigationResult(lines, [{'name': constraint_str}], linkage))
            # there will not full info about constraint
        return results

    @generate(
        # '001_most_basic',
        # '002_match_latest',
        '003_match_time_range',
        # '005_match_tree',
        # '006_match_parameter',
        # '007_match_or',
        # '008_match_and',
        # '009_match_negation',
        # '010_multiple_files',
        # '011_different_entry',
        # '012_multiple_rulebooks',
        # '013_match_and_incomplete',
    )
    def test_one(self, test_name):
        # paths files setup
        prefix_path = os.path.join(*TestPaths.path_test_files)
        path = os.path.join(prefix_path, test_name)
        input_path = os.path.join(path, 'input.txt')
        # output_path = os.path.join(path, 'expected_output.txt')  # FIXME is it really unnecessary?
        log_file = os.path.join(path, 'node_1.log')
        results_file = os.path.join(path, 'investigation_results.txt')

        # gathering information about effect line
        line_number = self._get_cause_line_number(input_path)
        line_content = self._get_concrete_line_from_file(log_file, line_number)
        effect_line_offset = self._deduce_line_offset(log_file, line_number)

        # preparing Whylog structures, normally prepared by Front
        whylog_config = YamlConfig(*ConfigPathFactory.get_path_to_config_files(path))
        log_reader = LogReader(whylog_config)
        line = FrontInput(effect_line_offset, line_content, prefix_path)

        # action and checking the result
        results = log_reader.get_causes(line)
        assert results
        true_results = self._investigation_results_from_file(log_file, results_file)
        for got, real in zip(results, true_results):
            assert got.lines == real.lines
            for constr_got, constr_real in zip(got.constraints, real.constraints):
                assert constr_got['name'] == constr_real['name']
