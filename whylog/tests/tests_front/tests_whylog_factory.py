from whylog.front.whylog_factory import whylog_factory
from whylog.log_reader import LogReader
from whylog.teacher import Teacher
from whylog.tests.utils import TestRemovingSettings


class TestWhylogFactory(TestRemovingSettings):
    def tests_whylog_factory(self):
        log_reader, teacher_generator = whylog_factory()
        teacher = teacher_generator()

        assert isinstance(log_reader, LogReader)
        assert isinstance(teacher, Teacher)
