from whylog.config.investigation_plan import LineSource
from whylog.front.whylog_factory import whylog_factory
from whylog.front.utils import FrontInput
from whylog.log_reader import LogReader
from whylog.teacher import Teacher
from whylog.tests.utils import TestRemovingSettings


class TestWhylogFactory(TestRemovingSettings):
    def tests_whylog_factory(self):
        log_reader, teacher_generator = whylog_factory()
        teacher = teacher_generator()

        front_input = FrontInput(1, 'line content', LineSource('host', 'path'))
        log_reader.get_causes(front_input)
        teacher.add_line(0, front_input, True)
