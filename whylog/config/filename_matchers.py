import glob
from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class AbstractFilenameMatcher(object):
    @abstractmethod
    def get_matched_files(self):
        pass


class WildCardFilenameMatcher(AbstractFilenameMatcher):
    def __init__(self, host_pattern, path_pattern, log_type_name):
        self.log_type_name = log_type_name
        self.path_pattern = path_pattern
        self.host_pattern = host_pattern

    def get_matched_files(self):
        if self.host_pattern == 'localhost':
            for path in glob.iglob(self.path_pattern):
                yield 'localhost', path
        else:
            # TODO: finding files in others hosts
            raise NotImplementedError

    def __repr__(self):
        return "(WildCardFilenameMatcher: %s, %s, %s)" % (
            self.log_type_name, self.path_pattern, self.host_pattern
        )


class WildCardFilenameMatcherFactory(object):
    @classmethod
    def from_dao(cls, serialized):
        del serialized['matcher_class_name']
        return WildCardFilenameMatcher(**serialized)
