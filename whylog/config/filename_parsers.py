from abc import ABCMeta, abstractmethod


class AbstractFilenameParser(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_file_names_to_parse(self):
        pass


class RegexFilenameParser(AbstractFilenameParser):
    def __init__(self, path_pattern):
        pass

    def get_file_names_to_parse(self):
        pass
