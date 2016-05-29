import os.path
from unittest import TestCase

import six
import yaml
from generator import generate, generator

from whylog.config import YamlConfig
from whylog.config.abstract_config import AbstractConfig
from whylog.config.investigation_plan import LineSource
from whylog.constraints.verifier import InvestigationResult
from whylog.front.utils import FrontInput
from whylog.log_reader import LogReader
from whylog.tests.tests_log_reader.constants import TestPaths
from whylog.tests.utils import ConfigPathFactory

from nose import SkipTest

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

    def _get_starting_file_name(self, input_info_file_path):
        return open(input_info_file_path).readline().split(":")[0].rstrip('\n')

    def _get_concrete_line_from_file(self, file_path, line_num):
        return [line.rstrip('\n') for line in open(file_path)][line_num]

    def _deduce_line_offset(self, file_path, line_no):
        """ returns offset of line 'line_no' in file 'file_path' """
        return sum([len(line) for line in open(file_path)][0:line_no])

    def _deduce_line_offset_by_unique_content(self, file_path, line_content):
        all_lines = [line.rstrip('\n') for line in open(file_path)]
        try:
            line_no = all_lines.index(line_content)
        except ValueError:
            raise ValueError("Not found line '%s' in file '%s'" % (line_content, file_path))
        return self._deduce_line_offset(file_path, line_no)

    def _get_last_line_from_file(self, file_path):
        return [line.rstrip('\n') for line in open(file_path)][-1]

    def _investigation_results_from_yaml(self, yaml_file, real_log_file):
        file_content = yaml.load(open(yaml_file))
        results = []
        for result in file_content:
            causes = [
                FrontInput(
                    self._deduce_line_offset_by_unique_content(real_log_file, line_str), line_str,
                    LineSource("localhost", real_log_file)
                ) for line_str in result['causes']
            ]  # yapf: disable
            results.append(InvestigationResult(causes, result['constraints'], result['linkage']))
        return results

    @classmethod
    def _check_results(cls, results, expected_results):
        # action and checking the result
        assert results
        assert len(results) == len(expected_results)
        for got, real in six.moves.zip(results, expected_results):
            assert got.lines == real.lines
            for constr_got, constr_real in zip(got.constraints, real.constraints):
                assert constr_got['name'] == constr_real['name']

    @generate(
        '001_most_basic',
        # '002_match_latest',
        '003_match_time_range',
        # '005_match_tree',
        '006_match_parameter',
        '007_match_or',
        '008_match_and',
        '009_match_negation',
        '010_multiple_files',
        '011_different_entry',
        # '012_multiple_rulebooks',
        # '013_match_and_incomplete',
    )  # yapf: disable
    def test_one(self, test_name):
        # paths files setup
        prefix_path = os.path.join(*TestPaths.path_test_files)
        path = os.path.join(prefix_path, test_name)
        input_path = os.path.join(path, 'input.txt')
        # output_path = os.path.join(path, 'expected_output.txt')  # FIXME is it really unnecessary?

        original_log_file = os.path.join(path, 'node_1.log')
        result_log_file = original_log_file
        if test_name == "010_multiple_files":
            result_log_file = os.path.join(path, 'node_2.log')
        if test_name == "011_different_entry":
            result_log_file = os.path.join(path, 'node_3.log')

        results_yaml_file = os.path.join(path, 'investigation_results.yaml')

        # gathering information about effect line
        line_number = self._get_cause_line_number(input_path)
        line_content = self._get_concrete_line_from_file(original_log_file, line_number)
        effect_line_offset = self._deduce_line_offset(original_log_file, line_number)

        # preparing Whylog structures, normally prepared by Front
        whylog_config = YamlConfig(*ConfigPathFactory.get_path_to_config_files(path))
        log_reader = LogReader(whylog_config)
        effect_line = FrontInput(
            effect_line_offset, line_content, LineSource(
                'localhost', os.path.join(path, self._get_starting_file_name(input_path))
            )
        )

        results = log_reader.get_causes(effect_line)
        expected_results = self._investigation_results_from_yaml(results_yaml_file, result_log_file)
        self._check_results(results, expected_results)

    @generate(
        '001_most_basic',
        # '002_match_latest',
        '003_match_time_range',
        # '005_match_tree',
        '006_match_parameter',
        '007_match_or',
        '008_match_and',
        '009_match_negation',
        '010_multiple_files',
        '011_different_entry',
        # '012_multiple_rulebooks',
        # '013_match_and_incomplete',
    )  # yapf: disable
    def test_temporary_file_assing_to_logtype(self, test_name):
        # paths files setup
        prefix_path = os.path.join(*TestPaths.path_test_files)
        path = os.path.join(prefix_path, test_name)
        input_path = os.path.join(path, 'input.txt')
        # output_path = os.path.join(path, 'expected_output.txt')  # FIXME is it really unnecessary?

        original_log_file = os.path.join(path, 'node_1.log')
        result_log_file = original_log_file
        if test_name == "010_multiple_files":
            result_log_file = os.path.join(path, 'node_2.log')
        if test_name == "011_different_entry":
            result_log_file = os.path.join(path, 'node_3.log')

        results_yaml_file = os.path.join(path, 'investigation_results.yaml')

        # gathering information about effect line
        line_number = self._get_cause_line_number(input_path)
        line_content = self._get_concrete_line_from_file(original_log_file, line_number)
        effect_line_offset = self._deduce_line_offset(original_log_file, line_number)

        # preparing Whylog structures, normally prepared by Front
        whylog_config = YamlConfig(*ConfigPathFactory.get_path_to_config_files(path))
        # Erasing saved log types
        whylog_config._log_types = {}
        log_reader = LogReader(whylog_config)
        effect_line = FrontInput(
            effect_line_offset, line_content, LineSource(
                'localhost', os.path.join(path, self._get_starting_file_name(input_path))
            )
        )

        node1_source = LineSource('localhost', os.path.join(path, 'node_1.log'))
        node2_source = LineSource('localhost', os.path.join(path, 'node_2.log'))
        node3_source = LineSource('localhost', os.path.join(path, 'node_3.log'))
        temp_assign = {AbstractConfig.DEFAULT_LOG_TYPE: [node1_source]}
        if test_name == "010_multiple_files":
            temp_assign = {AbstractConfig.DEFAULT_LOG_TYPE: [node1_source, node2_source]}
        if test_name == "011_different_entry":
            temp_assign = {AbstractConfig.DEFAULT_LOG_TYPE: [node1_source, node2_source, node3_source]}

        raise SkipTest
        results = log_reader.get_causes(effect_line, temp_assign)
        expected_results = self._investigation_results_from_yaml(results_yaml_file, result_log_file)
        self._check_results(results, expected_results)
