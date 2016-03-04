class NoDateGroupException(Exception):
    def __init__(self, line):
        self.line = line
        self.message = 'No date group in regex'

    def __str__(self):
        return self.message
