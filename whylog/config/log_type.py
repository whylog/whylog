class LogType(object):
    def __init__(self, name, filename_matchers):
        self.name = name
        self.filename_matchers = filename_matchers

    def files_to_parse(self):
        """
        Gets all possible distinct pairs (host, file_name) belonging to single log type
        It's information which files should be parsed by LogReader.
        """
        parsed_files = set()
        for matcher in self.filename_matchers:
            for file_source in matcher.get_matched_files():
                if file_source not in parsed_files:
                    parsed_files.add(file_source)
                    yield file_source

    def does_belong_to_log_type(self, line_source):
        return any(
            matcher.does_belong_to_matcher(line_source) for matcher in self.filename_matchers
        )
