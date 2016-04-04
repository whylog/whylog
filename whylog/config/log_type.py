class LogType(object):
    def __init__(self, name, filename_matchers):
        self._name = name
        self._filename_matchers = filename_matchers

    #It will be generator
    def get_next_file_to_parse(self):
        return 'localhost', 'node_1.log'
