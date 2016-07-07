from whylog.exceptions import WhylogError


class LogReaderError(WhylogError):
    pass


class NoLogTypeError(LogReaderError):
    def __init__(self, front_input):
        super(NoLogTypeError, self).__init__()
        self._front_input = front_input

    def __str__(self):
        return 'Config did not match any log_type to the specified front_input: %s; cannot investigate' % (
            self._front_input
        )


class EmptyFile(LogReaderError):
    pass


class OffsetBiggerThanFileSize(LogReaderError):
    def __init__(self, offset):
        super(OffsetBiggerThanFileSize, self).__init__()
        self.offset = offset

    def __str__(self):
        return 'Captured offset (%s) is too big' % self.offset
