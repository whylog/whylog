from functools import partial

from whylog.config import SettingsFactorySelector
from whylog.log_reader import LogReader
from whylog.teacher import Teacher


def whylog_factory():
    """
    This function returns LogReader object and teachers_generator.
    """
    settings = SettingsFactorySelector.get_settings()
    pattern_assistant = settings['assistant']()
    config = settings['config']
    return LogReader(config), partial(Teacher, config, pattern_assistant)
