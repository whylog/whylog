import datetime
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
                start_time=datetime.datetime(
                    year=2000,
                    month=1,
                    day=1
                ),
                time_delta=datetime.timedelta(milliseconds=cls.time_delta_ms),
                number_of_lines=cls.number_of_lines,
                line_padding=cls.line_padding,
                datetime_format="%c"
            )
        )  # yapf: disable
        cls.the_earliest_date = datetime.datetime(year=1, month=1, day=1)
        cls.the_soonest_date = datetime.datetime(year=2222, month=1, day=1)

    def test_bisect_line_finding(self):
        secs = 3
        millisecs = secs * 1000
        date = datetime.datetime(year=2000, month=1, day=1, second=secs)

        backtracker = BacktrackSearcher("")
        offset = backtracker._find_offset_by_date(self.opened_file, date)

        raise SkipTest('Not implemented yet')
        line_no = millisecs / self.time_delta_ms
        assert offset == line_no * self.line_padding

    def test_bisect_first_line_of_file(self):
        backtracker = BacktrackSearcher("")
        offset = backtracker._find_offset_by_date(self.opened_file, self.the_earliest_date)

        raise SkipTest('Not implemented yet')
        assert offset == 0

    def test_bisect_last_line_of_file(self):
        backtracker = BacktrackSearcher("")
        offset = backtracker._find_offset_by_date(self.opened_file, self.the_soonest_date)

        raise SkipTest('Not implemented yet')
        assert offset == (self.number_of_lines - 1) * self.line_padding
