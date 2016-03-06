class InvalidParserIndex(Exception):
    def __init__(self, cause_index):
        self.cause_index = cause_index

    def __str__(self):
        return 'No parser with index: %d' % self.cause_index
