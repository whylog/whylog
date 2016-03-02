from unittest import TestCase
import os.path
from .constants import AFewLinesLogParams

from whylog.client import searchers


class TestBacktrackSearcher(TestCase):
    def _get_log_file_path(self):
        prefix_path = os.path.join(*path_test_files)
        path = os.path.join(prefix_path, "a_few_lines.log")
        return path

    def _count_lines_in_file(self, file_name):
        return sum(1 for line in open(file_name))

    def _get_sample_offset(self, line_num):
        """
        Returns the correct offset of line 'line_num'
        referring to the file a_few_lines.log construction.
        Be careful when modifying a_few_lines.log.
        """
        assert line_num <= self._count_lines_in_file(self._get_log_file_path())
        return line_num * constants.AFewLinesLogParams.SINGLE_LINE_LENGTH

    def _read_all_lines_from_file(self, file_path):
        with open(file_path) as f:
            return f.read().splitlines()

    def _check_lines(self, lines_normally, lines_reversed):
        assert len(lines_reversed) == len(lines_normally)
        for i, j in zip(lines_reversed, reversed(lines_normally)):
            assert i == j

    def _sample_call_with_specified_bufsize(self, bufsize):
        log_file_path = self._get_log_file_path()

        how_many_lines = 7
        offset = self._get_sample_offset(how_many_lines)

        backtracker = searchers.BacktrackSearcher(log_file_path)

        lines = self._read_all_lines_from_file(log_file_path)[:how_many_lines]
        lines_reversed = list(backtracker._reverse_from_offset(offset, bufsize))

        self._check_lines(lines_reversed, lines)

    def test_very_small_bufsize(self):
        for i in range(1, 5):
            self._sample_call_with_specified_bufsize(i)

    def test_file_size_as_offset(self):
        log_file_path = self._get_log_file_path()

        file_size_as_offset = os.path.getsize(log_file_path)

        backtracker = searchers.BacktrackSearcher(log_file_path)

        lines = self._read_all_lines_from_file(log_file_path)
        lines_reversed = list(backtracker._reverse_from_offset(file_size_as_offset))

        self._check_lines(lines_reversed, lines)
