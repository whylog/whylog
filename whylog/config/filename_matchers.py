from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class AbstractFilenameMatcher(object):
    @abstractmethod
    def get_matched_logs(self):
        pass


class RegexFilenameMatcher(AbstractFilenameMatcher):
    def __init__(self, path_pattern):
        pass

    def get_matched_logs(self):
        pass
