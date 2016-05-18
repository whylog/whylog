from datetime import datetime, timedelta
from unittest import TestCase

from nose.plugins.skip import SkipTest

from whylog.log_reader.searchers import BacktrackSearcher
from whylog.tests.tests_log_reader.file_reader import (
    DataGeneratorLogSource, OperationCountingFileWrapper
)


class TestLogsReading(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.time_delta_ms = 100
        cls.number_of_lines = 10000
        cls.line_padding = 42
        cls.opened_file = OperationCountingFileWrapper(
            DataGeneratorLogSource(
                start_time=datetime(
                    year=2000,
                    month=1,
                    day=1
                ),
                time_delta=timedelta(milliseconds=cls.time_delta_ms),
                number_of_lines=cls.number_of_lines,
                line_padding=cls.line_padding,
                datetime_format="%c"
            )
        )  # yapf: disable

    def test_bisect_line_finding(self):
        secs = 3
        millisecs = secs * 1000
        date = datetime(year=2000, month=1, day=1, second=secs)

        backtracker = BacktrackSearcher("")
        offset = backtracker._find_offset(self.opened_file, date, {})

        raise SkipTest('Not implemented yet')
        line_no = millisecs / self.time_delta_ms
        assert offset == line_no * self.line_padding
        assert self.opened_file._seek_count < 30

    def test_bisect_first_line_of_file(self):
        backtracker = BacktrackSearcher("")
        offset = backtracker._find_offset(self.opened_file, datetime.min, {})

        raise SkipTest('Not implemented yet')
        assert offset == 0
        assert self.opened_file._seek_count < 30

    def test_bisect_last_line_of_file(self):
        backtracker = BacktrackSearcher("")
        offset = backtracker._find_offset(self.opened_file, datetime.max, {})

        raise SkipTest('Not implemented yet')
        assert offset == (self.number_of_lines - 1) * self.line_padding
        assert self.opened_file._seek_count < 30
