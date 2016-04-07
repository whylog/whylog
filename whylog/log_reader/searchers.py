from abc import ABCMeta, abstractmethod

import os.path
from os import SEEK_SET

import six

from whylog.log_reader.const import BufsizeConsts


@six.add_metaclass(ABCMeta)
class AbstractSearcher(object):
    @abstractmethod
    def search(self, search_data):
        """
        transfer investigation to searcher
        """
        pass


class IndexSearcher(AbstractSearcher):
    def search(self, search_data):
        pass


class DatabaseSearcher(AbstractSearcher):
    def search(self, search_data):
        pass


class BacktrackSearcher(AbstractSearcher):
    def __init__(self, file_path):
        self._file_path = file_path

    @classmethod
    def _extract_time_from_line(cls, line_str):
        """
        extracts time from line
        """
        pass  # TODO this function (or equivalent) should be written in config module

    def _deduce_offset(self, time):
        """
        returns offset of the line with the specified time
        """
        # for line in self._reverse_from_offset(os.path.getsize(self._file_path)):
        #     if self.get_time_from_line(line(0)) <= time:
        #         return line(1)
        return 69  # FIXME it is only mock for test 003

    def search(self, investigation_step):
        # TODO should be one such function per log file <- what?!?
        clues = {}
        offset = self._deduce_offset(investigation_step.effect_time)
        for line, actual_offset in self._reverse_from_offset(offset):
            one_clue_dict = investigation_step.get_clues(line, actual_offset)  # TODO check if line somehow fits
            # TODO ^ contains dict
            # TODO append information from clue to clues dict
        return clues

    @classmethod
    def _decrease_actual_offset_properly(cls, actual_offset, drop_string):
        return actual_offset - len(drop_string) - 1

    def _reverse_from_offset(self, offset, buf_size=BufsizeConsts.STANDARD_BUF_SIZE):
        """
        a generator that returns the pairs consisting of
        lines in reverse order and offsets corresponding to them,
        beginning with the specified offset
        """
        with open(self._file_path) as fh:
            fh.seek(offset)
            total_size = remaining_size = fh.tell()
            reverse_offset = 0
            actual_offset = offset
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
                        actual_offset = self._decrease_actual_offset_properly(
                            actual_offset, truncated
                        )
                        yield truncated, actual_offset
                truncated = lines[0]
                for line in reversed(lines[1:]):
                    if len(line):
                        actual_offset = self._decrease_actual_offset_properly(actual_offset, line)
                        yield line, actual_offset
            actual_offset = self._decrease_actual_offset_properly(actual_offset, truncated)
            yield truncated, actual_offset
