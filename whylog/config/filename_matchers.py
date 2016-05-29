import fnmatch
import glob
from abc import ABCMeta, abstractmethod

import six

from whylog.config.super_parser import RegexSuperParserFactory


@six.add_metaclass(ABCMeta)
class AbstractFilenameMatcher(object):
    @abstractmethod
    def get_matched_files(self):
        pass


class WildCardFilenameMatcher(AbstractFilenameMatcher):
    def __init__(self, host_pattern, path_pattern, log_type_name, super_parser):
        self.host_pattern = host_pattern
        self.path_pattern = path_pattern
        self.log_type_name = log_type_name
        self.super_parser = super_parser

    def get_matched_files(self):
        print self.host_pattern
        if self.host_pattern == 'localhost':
            for path in glob.iglob(self.path_pattern):
                yield 'localhost', path, self.super_parser
        else:
            # TODO: finding files in others hosts
            raise NotImplementedError

    def __contains__(self, line_source):
        return fnmatch.fnmatch(line_source.host, self.host_pattern) and fnmatch.fnmatch(
            line_source.path, self.path_pattern
        )

    def serialize(self):
        return {
            'matcher_class_name': "WildCardFilenameMatcher",
            'log_type_name': self.log_type_name,
            'path_pattern': self.path_pattern,
            'host_pattern': self.host_pattern,
            'super_parser': self.super_parser.serialize()
        }

    def __repr__(self):
        return "(WildCardFilenameMatcher: %s, %s, %s)" % (
            self.log_type_name, self.path_pattern, self.host_pattern
        )


class WildCardFilenameMatcherFactory(object):
    @classmethod
    def from_dao(cls, serialized):
        del serialized['matcher_class_name']
        super_parser_definition = serialized['super_parser']
        serialized['super_parser'] = RegexSuperParserFactory.from_dao(super_parser_definition)
        return WildCardFilenameMatcher(**serialized)
