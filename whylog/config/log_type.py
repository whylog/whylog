class LogType(object):
    def __init__(self, name, filename_matchers):
        self.name = name
        self.filename_matchers = filename_matchers

    def files_to_parse(self):
        """
        Gets all possible distinct pairs (host, file_name) belongs to single log type
        It's information for LogReader which files should be parsed by its.
        """
        parsed_files = set()
        for matcher in self.filename_matchers:
            for file_source in matcher.get_matched_files():
                if file_source not in parsed_files:
                    parsed_files.add(file_source)
                    yield file_source
