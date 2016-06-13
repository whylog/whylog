from abc import ABCMeta, abstractmethod
from collections import defaultdict
from os import SEEK_SET

import six

from whylog.config.investigation_plan import InvestigationStep, LineSource
from whylog.config.utils import CompareResult
from whylog.log_reader.const import BufsizeConsts
from whylog.log_reader.read_utils import ReadUtils


@six.add_metaclass(ABCMeta)
class AbstractSearcher(object):
    @abstractmethod
    def search(self, original_front_input):
        """
        transfer investigation to searcher
        """
        pass


class IndexSearcher(AbstractSearcher):
    def search(self, original_front_input):
        pass


class DatabaseSearcher(AbstractSearcher):
    def search(self, original_front_input):
        pass


class BacktrackSearcher(AbstractSearcher):
    def __init__(self, file_path, investigation_step, super_parser):
        self._file_path = file_path
        self._investigation_step = investigation_step
        self._super_parser = super_parser

    def _find_left(self, opened_file):
        left = 0
        right = ReadUtils.size_of_opened_file(opened_file)
        while left + 1 < right:
            curr = (left + right) // 2
            line, line_begin, line_end = ReadUtils.get_line_containing_offset(
                opened_file, curr, ReadUtils.STANDARD_BUFFER_SIZE
            )
            groups = self._super_parser.get_ordered_groups(line)
            assert len(groups) <= 1
            if self._investigation_step.compare_with_bound(
                InvestigationStep.LEFT_BOUND, groups
            ) == CompareResult.LT:
                # omit actual line and go right
                left = line_end + 1
            else:
                # going left, omit actual line, but maybe it will be returned
                right = line_begin
        return right

    def _find_right(self, opened_file):
        left = 0
        right = ReadUtils.size_of_opened_file(opened_file)
        while left + 1 < right:
            curr = (left + right) // 2
            line, line_begin, line_end = ReadUtils.get_line_containing_offset(
                opened_file, curr, ReadUtils.STANDARD_BUFFER_SIZE
            )
            groups = self._super_parser.get_ordered_groups(line)
            assert len(groups) <= 1
            if self._investigation_step.compare_with_bound(InvestigationStep.RIGHT_BOUND, groups)\
                    in [CompareResult.LT, CompareResult.EQ]:
                # go to the end of current line, maybe it will be returned
                left = line_end
            else:
                # going left, current line is not interesting
                right = line_begin - 1
        if right == 0:
            return 0
        _, _, end_offset = ReadUtils.get_line_containing_offset(
            opened_file, right - 1, ReadUtils.STANDARD_BUFFER_SIZE
        )
        return end_offset + 1

    def _find_offsets_range(self, original_front_input):
        """
        returns a pair of offsets between whose the investigation
        in file should be provided
        """
        with open(self._file_path) as fd:
            left_bound = self._find_left(fd)
            if original_front_input.line_source.path == self._file_path:
                right_bound = original_front_input.offset
            else:
                right_bound = self._find_right(fd)
        return left_bound, right_bound

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

    def search(self, original_front_input):
        clues = defaultdict(list)
        left_bound, right_bound = self._find_offsets_range(original_front_input)
        for line, actual_offset in self._reverse_from_offset(right_bound):
            if actual_offset < left_bound:
                return clues
            line_source = LineSource('localhost', self._file_path)
            clues_from_line = self._investigation_step.get_clues(line, actual_offset, line_source)
            self._merge_clues(clues, clues_from_line)
        return clues
