import datetime
from unittest import TestCase

from whylog.tests.tests_log_reader.file_reader import DataGeneratorLogSource, OperationCountingFileWrapper


class TestLogsReading(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.opened_file = OperationCountingFileWrapper(
            DataGeneratorLogSource(
                datetime.datetime(
                    year=2000,
                    month=1,
                    day=1
                ),
                datetime.timedelta(milliseconds=1),
                10000,
                42,
                "%c"
            )
        )  # yapf: disable

    def test_bisect_line_finding(self):
        pass
