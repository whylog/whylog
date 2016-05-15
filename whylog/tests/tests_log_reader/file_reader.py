import datetime


class OpenedLogsFile(object):
    def __init__(self, start_time, time_interval, log_file_size, line_padding):
        self._start_time = start_time
        self._time_interval = time_interval
        self._log_file_size = log_file_size
        self._line_padding = line_padding
        self._position = 0

    @classmethod
    def _repeat(cls, n, sign="r"):
        return sign * n

    def _deduce_line_no(self, offset):
        return offset / self._line_padding

    def _get_line(self, line_no):
        current_line_time = self._start_time + line_no * self._time_interval
        current_line_time_str = str(current_line_time) + " "
        current_line = current_line_time_str + self._repeat(
            self._line_padding - len(current_line_time_str) - 1
        ) + "\n"
        return current_line

    def _line_lying_on_offset(self, offset):
        line_no = self._deduce_line_no(offset)
        return self._get_line(line_no)

    def read(self, size):
        first_line_no = self._deduce_line_no(self._position)
        last_line_no = self._deduce_line_no(self._position + size)
        if first_line_no == last_line_no:
            line = self._get_line(first_line_no)
            position_in_line = self._position % self._line_padding
            return line[position_in_line:position_in_line + size]
        else:
            return "egg"  # TODO: implement this case

    def seek(self, offset, whence=0):
        if whence == 0:
            self._position = offset
        elif whence == 1:
            self._position += offset
        elif whence == 2:
            self._position = self._log_file_size - offset
        else:
            assert False

fh = OpenedLogsFile(
    datetime.datetime(year=2000, month=1, day=1),
    datetime.timedelta(microseconds=100),
    1000000,
    42
)
fh.seek(3)
fh.read(8)
