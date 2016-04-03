from abc import ABCMeta, abstractmethod

import re
import six


@six.add_metaclass(ABCMeta)
class AbstractFilenameMatcher(object):
    @abstractmethod
    def get_matched_logs(self):
        pass


class RegexFilenameMatcher(AbstractFilenameMatcher):
    def __init__(self, host_pattern, path_pattern, log_type_name):
        self.log_type_name = log_type_name
        self._path_pattern = path_pattern
        self._host_pattern = host_pattern
        self._host_regex = re.compile(host_pattern)
        self._path_regex = re.compile(path_pattern)

    def get_matched_logs(self):
        return ['node_1.log']
