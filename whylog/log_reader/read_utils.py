import os

from whylog.log_reader.exceptions import EmptyFile, OffsetBiggerThanFileSize


class ReadUtils(object):
    STANDARD_BUFFER_SIZE = 512

    @classmethod
    def size_of_opened_file(cls, fh):
        prev_position = fh.tell()
        fh.seek(0, os.SEEK_END)
        size = fh.tell()
        fh.seek(prev_position)
        return size

    @classmethod
    def _read_content(cls, fd, position, buf_size):
        fd.seek(position)
        return fd.read(buf_size)

    @classmethod
    def _read_split_lines(cls, fd, position, buf_size):
        content = cls._read_content(fd, position, buf_size)
        return content.split('\n')

    @classmethod
    def _join_results(cls, first_part, second_part):
        if not first_part:
            if not second_part:
                return []
            return second_part
        if not second_part:
            return first_part
        return first_part[:-1] + ["".join((first_part[-1], second_part[0]))] + second_part[1:]

    @classmethod
    def _expand_after(cls, fd, position):
        fd.seek(position)
        line = fd.readline()
        if not line:
            raise OffsetBiggerThanFileSize(position)
        return line.rstrip('\n')

    @classmethod
    def _expand_before(cls, fd, position, buf_size):
        before = []
        while len(before) < 2:
            position -= buf_size
            if position <= 0:
                lines = cls._read_split_lines(fd, 0, position + buf_size)
                before = cls._join_results(lines, before)
                break
            lines = cls._read_split_lines(fd, position, buf_size)
            before = cls._join_results(lines, before)
        if not before:
            raise EmptyFile()
        return before[-1]

    @classmethod
    def _read_entire_line(cls, fd, offset, buf_size):
        after = cls._expand_after(fd, offset)
        before = cls._expand_before(fd, offset, buf_size)
        return before + after, offset - len(before), offset + len(after)

    @classmethod
    def get_line_containing_offset(cls, fd, offset, buf_size):
        """
        returns line which contains the specified offset
        and returns also offsets of the first and the last sign of this line.
        if there is '\n' on specified offset, the previous line is returned
        """
        return cls._read_entire_line(fd, offset, buf_size)
