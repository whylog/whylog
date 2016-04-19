import re
from abc import ABCMeta, abstractmethod
import glob

import six


@six.add_metaclass(ABCMeta)
class AbstractFilenameMatcher(object):
    @abstractmethod
    def get_matched_files(self):
        pass


class RegexFilenameMatcher(AbstractFilenameMatcher):
    def __init__(self, host_pattern, path_pattern, log_type_name):
        self.log_type_name = log_type_name
        self._path_pattern = path_pattern
        self._host_pattern = host_pattern
        self._host_regex = re.compile(host_pattern)
        self._path_regex = re.compile(path_pattern)

    def get_matched_files(self):
        # TODO: remove mock
        return ['node_1.log']


class RegexFilenameMatcherFactory(object):
    @classmethod
    def from_dao(cls, serialized):
        del serialized['matcher_class_name']
        return RegexFilenameMatcher(**serialized)


class WildCardFilenameMatcher(AbstractFilenameMatcher):
    def __init__(self, host_pattern, path_pattern, log_type_name):
        self.log_type_name = log_type_name
        self._path_pattern = path_pattern
        self._host_pattern = host_pattern

    def get_matched_files(self):
        if self._host_pattern == 'localhost':
            return glob.glob(self._path_pattern)
        else:
            #TODO: finding files in others hosts
            pass
