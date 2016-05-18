class LogType(object):
    def __init__(self, name, filename_matchers):
        self.name = name
        self.filename_matchers = filename_matchers

    def files_to_parse(self):
        """
        Gets all possible distinct tuples (host, file_name, super_parser) belonging to single log type
        It's information which files should be parsed by LogReader. Super parser has a information about
        inner log file structure
        """
        parsed_files = set()
        for matcher in self.filename_matchers:
            for host, path, super_parser in matcher.get_matched_files():
                file_source = (host, path)
                if file_source not in parsed_files:
                    parsed_files.add(file_source)
                    yield host, path, super_parser

    def __contains__(self, line_source):
        return any(line_source in matcher for matcher in self.filename_matchers)

    def __repr__(self):
        return "(LogType: %s %s)" % (self.name, self.filename_matchers)
