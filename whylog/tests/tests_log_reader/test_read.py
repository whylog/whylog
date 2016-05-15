from unittest import TestCase
import datetime

from whylog.tests.tests_log_reader.file_reader import OpenedLogsFile


class TestLogsReading(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.opened_file = OpenedLogsFile(
            datetime.datetime(year=2000, month=1, day=1),
            datetime.timedelta(microseconds=100),
            10000,
            42
        )

    def test_bisect_line_finding(self):
        pass
