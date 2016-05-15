import datetime
from unittest import TestCase

from whylog.tests.tests_log_reader.file_reader import OpenedFile, OpenedLogsFile


class TestLogsReading(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.opened_file = OpenedLogsFile(
            OpenedFile(
                datetime.datetime(
                    year=2000,
                    month=1,
                    day=1
                ),
                datetime.timedelta(microseconds=100),
                10000,
                42
            )
        )  # yapf: disable

    def test_bisect_line_finding(self):
        pass
