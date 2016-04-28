class LogType(object):
    def __init__(self, name, filename_matchers):
        self.name = name
        self.filename_matchers = filename_matchers

    def files_to_parse(self):
        for matcher in self.filename_matchers:
            for host, path in matcher.get_matched_files():
                yield host, path
