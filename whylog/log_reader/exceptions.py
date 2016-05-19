from whylog.exceptions import WhylogError


class LogReaderError(WhylogError):
    pass


class NoLogTypeError(LogReaderError):
    def __init__(self, front_input):
        self._front_input = front_input

    def __str__(self):
        return 'Config did not match any log_type to the specified front_input: %s; cannot investigate' % (
            self._front_input
        )


class ReadingError(LogReaderError):
    def __init__(self, info):
        self.info = info

    def __str__(self):
        return 'Read error: %s' % self.info
