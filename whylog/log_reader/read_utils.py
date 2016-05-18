class ReadUtils(object):
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
        return first_part[:-1] + ["".join([first_part[-1], second_part[0]])] + second_part[1:]

    @classmethod
    def _expand_left(cls, fd, position, buf_size):
        after = []
        while len(after) < 2:
            lines = cls._read_split_lines(fd, position, buf_size)
            if lines == ['']:
                break
            after = cls._join_results(after, lines)
            position += buf_size
        return after

    @classmethod
    def _expand_right(cls, fd, position, buf_size):
        before = []
        while len(before) < 2:
            position -= buf_size
            if position <= 0:
                lines = cls._read_split_lines(fd, 0, position + buf_size)
                before = cls._join_results(lines, before)
                break
            lines = cls._read_split_lines(fd, position, buf_size)
            before = cls._join_results(lines, before)
        return before

    @classmethod
    def _read_entire_line(cls, fd, offset, buf_size):
        after = cls._expand_left(fd, offset, buf_size)
        before = cls._expand_right(fd, offset, buf_size)
        if not before:
            raise Exception("Empty file!")
        if not after:
            raise Exception("Offset bigger than file size!")
        return before[-1] + after[0]

    @classmethod
    def get_line_containing_offset(cls, fd, offset, buf_size):
        return cls._read_entire_line(fd, offset, buf_size)
