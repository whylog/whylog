import itertools

from whylog.config.super_parser import RegexSuperParser

DEFAULT_SUPER_REGEX = RegexSuperParser("", [], {})
EMPTY_TUPLE = tuple()


class LogType(object):
    def __init__(self, name, filename_matchers):
        self.name = name
        self.filename_matchers = filename_matchers

    def files_to_parse(self, forced_log_type=None):
        """
        Gets all possible distinct tuples (host, file_name, super_parser) belonging to single log type
        It's information which files should be parsed by LogReader. Super parser has a information about
        inner log file structure
        """
        forced_log_type = forced_log_type or EMPTY_TUPLE
        parsed_files = set()
        for matcher in self.filename_matchers:
            for host, path, super_parser in itertools.chain(
                self._generate_forced_files(
                    forced_log_type
                ), matcher.get_matched_files()
            ):
                file_source = (host, path)
                if file_source not in parsed_files:
                    parsed_files.add(file_source)
                    yield host, path, super_parser

    @classmethod
    def _generate_forced_files(cls, forced_log_type):
        return (
            (
                line_source.host, line_source.path, DEFAULT_SUPER_REGEX
            ) for line_source in forced_log_type
        )

    def __hash__(self):
        return self.name.__hash__()

    def __eq__(self, other):
        return self.name == other.name

    def __contains__(self, line_source):
        return any(line_source in matcher for matcher in self.filename_matchers)

    def __repr__(self):
        return "(LogType: %s %s)" % (self.name, self.filename_matchers)
