import fnmatch
import glob
from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class AbstractFilenameMatcher(object):
    @abstractmethod
    def get_matched_files(self):
        pass

    @abstractmethod
    def is_belong_to_matcher(self, line_source):
        pass


class WildCardFilenameMatcher(AbstractFilenameMatcher):
    def __init__(self, host_pattern, path_pattern, log_type_name):
        self.host_pattern = host_pattern
        self.path_pattern = path_pattern
        self.log_type_name = log_type_name

    def get_matched_files(self):
        if self.host_pattern == 'localhost':
            for path in glob.iglob(self.path_pattern):
                yield 'localhost', path
        else:
            # TODO: finding files in others hosts
            raise NotImplementedError

    def is_belong_to_matcher(self, line_source):
        return fnmatch.fnmatch(line_source.host, self.host_pattern) and fnmatch.fnmatch(
            line_source.path, self.path_pattern
        )

    def serialize(self):
        return {
            'matcher_class_name': "WildCardFilenameMatcher",
            'log_type_name': self.log_type_name,
            'path_pattern': self.path_pattern,
            'host_pattern': self.host_pattern,
        }

    def __repr__(self):
        return "(WildCardFilenameMatcher: %s, %s, %s)" % (
            self.log_type_name, self.path_pattern, self.host_pattern
        )


class WildCardFilenameMatcherFactory(object):
    @classmethod
    def from_dao(cls, serialized):
        del serialized['matcher_class_name']
        return WildCardFilenameMatcher(**serialized)
