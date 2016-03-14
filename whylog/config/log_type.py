import re


class LogType(object):
    def __init__(self, name, filename_matcher_class_name, host_pattern, path_pattern):
        self._name = name
        self._filename_matcher_class_name = filename_matcher_class_name
        self._host_pattern_str = host_pattern
        self._path_pattern_str = path_pattern
        self._host_regex = re.compile(self._host_pattern_str)
        self._path_p = re.compile(self._host_pattern_str)

    def serialize(self):
        return {
            "name": self._name,
            "filename_matcher_class_name": self._filename_matcher_class_name,
            "host_pattern": self._host_pattern,
            "path_pattern": self._path_pattern,
        }


class LogTypeFactory(object):
    @classmethod
    def from_dao(cls, serialized_log_type):
        return LogType(**serialized_log_type)
