from datetime import datetime, timedelta
from unittest import TestCase

import six

from whylog.log_reader.read_utils import ReadUtils
from whylog.log_reader.searchers import BacktrackSearcher
from whylog.tests.tests_log_reader.constants import AFewLinesLogParams, TestPaths
from whylog.tests.tests_log_reader.file_reader import (
    DataGeneratorLogSource, OperationCountingFileWrapper
)


class TestLogsReading(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.time_delta_s = 1
        cls.number_of_lines = 10000
        cls.line_padding = 42
        cls.opened_file = OperationCountingFileWrapper(
            DataGeneratorLogSource(
                start_time=datetime(
                    year=2000,
                    month=1,
                    day=1
                ),
                time_delta=timedelta(seconds=cls.time_delta_s),
                number_of_lines=cls.number_of_lines,
                line_padding=cls.line_padding,
                datetime_format="%c"
            )
        )  # yapf: disable

    def test_getting_line_by_offset_huge(self):
        with open(TestPaths.get_file_path(AFewLinesLogParams.FILE_NAME)) as fh:
            for j in six.moves.range(1, 120, 7):
                for i in six.moves.range(100):
                    assert ReadUtils.get_line_containing_offset(fh, i, j) == \
                           AFewLinesLogParams.get_line_with_borders(i)

    def test_getting_line_by_offset_basic(self):
        with open(TestPaths.get_file_path(AFewLinesLogParams.FILE_NAME)) as fh:
            read_line = ReadUtils._read_entire_line(fh, 2, 10)
            assert read_line == ('aaa-0-bbb', 0, 9)
            read_line = ReadUtils._read_entire_line(fh, 2, 200)
            assert read_line == ('aaa-0-bbb', 0, 9)
            read_line = ReadUtils._read_entire_line(fh, 42, 10)
            assert read_line == ('aaa-4-bbb', 40, 49)
            read_line = ReadUtils._read_entire_line(fh, 99, 10)
            assert read_line == ('aaa-9-bbb', 90, 99)

    def test_bisect_line_finding(self):
        secs = 3
        date = datetime(year=2000, month=1, day=1, second=secs)

        backtracker = BacktrackSearcher("", None, None)
        offset = backtracker._find_left(self.opened_file, date, {})

        assert offset == secs * self.line_padding
        assert self.opened_file._seek_count < 100

    def test_bisect_first_line_of_file(self):
        backtracker = BacktrackSearcher("", None, None)
        offset = backtracker._find_left(self.opened_file, datetime.min, {})

        assert offset == 0
        assert self.opened_file._seek_count < 100

    def test_bisect_last_line_of_file(self):
        backtracker = BacktrackSearcher("", None, None)
        offset = backtracker._find_right(self.opened_file, datetime.max, {})

        assert offset == (self.number_of_lines - 1) * self.line_padding
        assert self.opened_file._seek_count < 100
