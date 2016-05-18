import itertools
import os

import six


class DataGeneratorLogSource(object):
    def __init__(self, start_time, time_delta, number_of_lines, line_padding, datetime_format):
        self._start_time = start_time
        self._time_delta = time_delta
        self._number_of_lines = number_of_lines
        self._line_padding = line_padding
        self._datetime_format = datetime_format
        self._position = 0

    def _deduce_line_no(self, offset):
        return offset / self._line_padding

    def _position_in_line(self, offset):
        return offset % self._line_padding

    def _get_line(self, line_no):
        current_line_time = self._start_time + line_no * self._time_delta
        current_line_time_str = current_line_time.strftime(self._datetime_format) + " "
        current_line = "%s %s\n" % (
            current_line_time.strftime(self._datetime_format),
            (self._line_padding - len(current_line_time_str) - 1) * "r"
        )
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
        return (self._get_line(no) for no in six.moves.range(first + 1, last))

    def read(self, size):
        assert size >= 0
        first_line_no = self._deduce_line_no(self._position)
        last_line_no = self._deduce_line_no(self._position + size)
        assert last_line_no < self._number_of_lines
        if first_line_no == last_line_no:
            line = self._get_line(first_line_no)
            position_in_line = self._position_in_line(self._position)
            result = line[position_in_line:position_in_line + size]
        else:
            first_line_position = self._position_in_line(self._position)
            first_line_fragment = self._get_line(first_line_no)[first_line_position:]
            last_line_position = self._position_in_line(self._position + size)
            last_line_fragment = self._get_line(last_line_no)[:last_line_position]
            lines_between = self._get_all_lines_between(first_line_no, last_line_no)
            content = "".join(
                itertools.chain(
                    (first_line_fragment,), lines_between, (last_line_fragment,)
                )
            )
            result = content
        self._position += size
        return result

    def tell(self):
        return self._position

    def seek(self, offset, whence=os.SEEK_SET):
        if whence == os.SEEK_SET:
            self._position = offset
        elif whence == os.SEEK_CUR:
            self._position += offset
        elif whence == os.SEEK_END:
            self._position = (self._number_of_lines * self._line_padding) - offset
        else:
            assert False


class OperationCountingFileWrapper(object):
    def __init__(self, file_object):
        self._opened_file = file_object
        self._seek_count = 0
        self._read_bytes = 0

    def read(self, *args):
        ret = self._opened_file.read(*args)
        self._read_bytes += len(ret)
        return ret

    def tell(self):
        return self._opened_file.tell()

    def seek(self, *args):
        self._seek_count += 1
        self._opened_file.seek(*args)
