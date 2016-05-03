import os.path
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from os import SEEK_SET

import six

from whylog.config.investigation_plan import LineSource
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

    def _deduce_offset(self, investigation_step):
        """
        returns offset of the line with the specified time
        """
        for line in self._reverse_from_offset(os.path.getsize(self._file_path)):
            line_content, line_offset = line
            if investigation_step.is_line_in_search_range(line_content):
                return line_offset

    @classmethod
    def _merge_clues(cls, collector, clues_from_line):
        for parser_name, clue in six.iteritems(clues_from_line):
            collector[parser_name].append(clue)

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
            if truncated:
                actual_offset = self._decrease_actual_offset_properly(actual_offset, truncated)
                yield truncated, actual_offset

    def search(self, investigation_step):
        clues = defaultdict(list)
        offset = self._deduce_offset(investigation_step)
        for line, actual_offset in self._reverse_from_offset(offset):
            # TODO: line_source object should be also passed into get_clues function
            # TODO: remove mock
            line_source = LineSource('localhost', 'node_1.log')
            clues_from_line = investigation_step.get_clues(line, actual_offset, line_source)
            self._merge_clues(clues, clues_from_line)
        return clues
