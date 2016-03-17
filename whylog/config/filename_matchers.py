from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class AbstractFilenameMatcher(object):
    @abstractmethod
    def get_matched_logs(self):
        pass


class RegexFilenameMatcher(AbstractFilenameMatcher):
    def __init__(self, host_pattern, path_pattern):
        self._host_regex = re.compile(host_pattern)
        self._path_regex = re.compile(host_pattern)

    def get_matched_logs(self):
        pass
