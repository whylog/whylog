from abc import ABCMeta, abstractmethod
from os import SEEK_SET


class AbstractSearcher(object):
    pass


class IndexSearcher(AbstractSearcher):
    pass


class DatabaseSearcher(AbstractSearcher):
    pass


class BacktrackSearcher(AbstractSearcher):
    def __init__(self, file_path):
        self._file_path = file_path

    def _reverse_from_offset(self, offset, buf_size=8192):
        """
		a generator that returns the lines of a file in reverse order
		beginning with the specified offset
		"""
        with open(self._file_path) as fh:
            fh.seek(offset)
            total_size = remaining_size = fh.tell()
            reverse_offset = 0
            truncated = None
            while remaining_size > 0:
                reverse_offset = min(total_size, reverse_offset + buf_size)
                fh.seek(total_size - reverse_offset, SEEK_SET)
                buffer_ = fh.read(min(remaining_size, buf_size))
                lines = buffer_.split('\n')
                remaining_size -= buf_size
                if truncated is not None:
                    if buffer_[-1] is not '\n':
                        lines[-1] += truncated
                    else:
                        yield truncated
                truncated = lines[0]
                for index in range(len(lines) - 1, 0, -1):
                    if len(lines[index]):
                        yield lines[index]
            yield truncated
