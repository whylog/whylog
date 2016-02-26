from abc import ABCMeta, abstractmethod


class AbstractFilenameMatcher(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_file_names_to_parse(self):
        pass


class RegexFilenameMatcher(AbstractFilenameMatcher):
    def __init__(self, path_pattern):
        pass

    def get_file_names_to_parse(self):
        pass
