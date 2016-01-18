from os.path import join as path_join
from unittest import TestCase

from generator import generate, generator
from nose.plugins.skip import SkipTest

from whylog.config import YamlConfig
from whylog.client import WhylogClient, searchers


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
        # whylog_client = WhylogClient(rulesbase=whylog_base, open_path=path)

        with open(input_path, 'r') as f:
            vim_line = f.read()
        # TODO call get_cause with sens...
        # result = whylog_client.get_cause(1, vim_line)

        raise SkipTest('Not implemented yet')
        with open(output_path, 'r') as f:
            pass
            # remove this comment after implement whylog client and base
            # assert result == f.read()


class TestBacktrackSearcher(TestCase):
    def test_imports_correctness(self):
        FOO_BAR = "/foo/bar"
        client = WhylogClient(rulesbase=WhylogBase())
        bts = searchers.BacktrackSearcher(file_path=FOO_BAR)
        assert bts._file_path == FOO_BAR

    def _get_log_file_path(self):
        client_tests_path = "/".join(path_test_files)
        return "%s/a_few_lines.log" % client_tests_path

    def _get_sample_offset(self, line_num):
        """
        Returns the correct offset of line 'line_num'
        referring to the file a_few_lines.log construction.
        Be careful when modifying a_few_lines.log.
        """
        line_length = 10
        return line_num * line_length

    def _reverse_from_offset_wrapper(self, backtracker, offset, buf_size=None):
        if buf_size == None:
            return [line for line in backtracker._reverse_from_offset(offset)]
        return [line for line in backtracker._reverse_from_offset(offset, buf_size)]

    def _read_all_lines_from_file(self, file_path):
        with open(file_path) as f:
            return f.read().splitlines()

    def _check_lines(self, lines_normally, lines_reversed):
        assert len(lines_reversed) == len(lines_normally)
        for i, j in zip(lines_reversed, reversed(lines_normally)):
            assert i == j

    def test_basic(self):
        self._sample_call()

    def _sample_call(self):
        self._sample_call_with_specified_bufsize(None)

    def _sample_call_with_specified_bufsize(self, bufsize):
        log_file_path = self._get_log_file_path()

        how_many_lines = 7
        offset = self._get_sample_offset(how_many_lines)

        backtracker = searchers.BacktrackSearcher(log_file_path)

        lines = self._read_all_lines_from_file(log_file_path)[:how_many_lines]
        lines_reversed = self._reverse_from_offset_wrapper(backtracker, offset, bufsize)

        self._check_lines(lines_reversed, lines)

    def test_very_small_bufsize(self):
        self._sample_call_with_specified_bufsize(4)
        self._sample_call_with_specified_bufsize(3)
        self._sample_call_with_specified_bufsize(2)
        self._sample_call_with_specified_bufsize(1)

    def _get_file_size(self, file_path):
        with open(file_path) as f:
            f.seek(0, 2)
            return f.tell()

    def test_file_size_as_offset(self):
        log_file_path = self._get_log_file_path()

        file_size_as_offset = self._get_file_size(log_file_path)

        backtracker = searchers.BacktrackSearcher(log_file_path)

        lines = self._read_all_lines_from_file(log_file_path)
        lines_reversed = self._reverse_from_offset_wrapper(backtracker, file_size_as_offset)

        self._check_lines(lines_reversed, lines)
