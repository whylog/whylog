import six


class OpenedFile(object):
    def __init__(self, start_time, time_interval, number_of_lines, line_padding):
        self._start_time = start_time
        self._time_interval = time_interval
        self._number_of_lines = number_of_lines
        self._line_padding = line_padding
        self._position = 0

    @classmethod
    def _repeat(cls, n, sign="r"):
        return sign * n

    def _deduce_line_no(self, offset):
        return offset / self._line_padding

    def _position_in_line(self, offset):
        return offset % self._line_padding

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

    def _get_all_lines_between(self, first, last):
        """
        except first and last,
        e.g. for first=3, last=6, the function
        returns lines 4th and 5th
        """
        return [self._get_line(no) for no in six.moves.range(first + 1, last)]

    def read(self, size):
        assert size >= 0
        first_line_no = self._deduce_line_no(self._position)
        last_line_no = self._deduce_line_no(self._position + size)
        assert last_line_no < self._number_of_lines
        if first_line_no == last_line_no:
            line = self._get_line(first_line_no)
            position_in_line = self._position_in_line(self._position)
            return line[position_in_line:position_in_line + size]
        else:
            first_line_position = self._position_in_line(self._position)
            first_line_fragment = self._get_line(first_line_no)[first_line_position:]
            last_line_position = self._position_in_line(self._position + size)
            last_line_fragment = self._get_line(last_line_no)[:last_line_position]
            lines_between = self._get_all_lines_between(first_line_no, last_line_no)
            content = "".join([first_line_fragment] + lines_between + [last_line_fragment])
            return content

    def tell(self):
        return self._position

    def seek(self, offset, whence=0):
        if whence == 0:
            self._position = offset
        elif whence == 1:
            self._position += offset
        elif whence == 2:
            self._position = (self._number_of_lines * self._line_padding) - offset
        else:
            assert False


class OpenedLogsFile(object):
    def __init__(self, *args):
        self._opened_file = OpenedFile(*args)
        self._seek_count = 0

    def read(self, *args):
        return self._opened_file.read(*args)

    def tell(self):
        return self._opened_file.tell()

    def seek(self, *args):
        self._seek_count += 1
        self._opened_file.seek(*args)
