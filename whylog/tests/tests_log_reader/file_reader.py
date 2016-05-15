import datetime


class OpenedLogsFile(object):
    def __init__(self, start_time, log_file_size, line_padding):
        self._start_time = start_time
        self._log_file_size = log_file_size
        self._line_padding = line_padding
        self._position = 0

    def read(self, size):
        return "0" * size  # TODO: implement this

    def seek(self, offset, whence=0):
        if whence == 0:
            self._position = offset
        elif whence == 1:
            self._position += offset
        elif whence == 2:
            self._position = self._log_file_size - offset
        else:
            raise Exception("Unrecognized option")
