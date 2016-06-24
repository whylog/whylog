from operator import attrgetter

from whylog.assistant.ranges import complementary_ranges
from whylog.assistant.span import Span
from whylog.exceptions import WhylogError


class OverlappingSpansError(WhylogError):
    def __init__(self, span1, span2):
        super(OverlappingSpansError, self).__init__()
        self.span1 = span1
        self.span2 = span2

    def __str__(self):
        return "%s overlaps %s" % (self.span1, self.span2)


class SpanList(list):
    def __add__(self, other):
        return SpanList(super(SpanList, self).__add__(other))

    def sort_by_start_and_end(self):
        return SpanList(sorted(self, key=attrgetter('start', 'end')))

    def sort_reversed_by_length(self):
        # we prefer longer dates, because it is safer (date is different in each log)
        return SpanList(sorted(self, key=attrgetter('length'), reverse=True))

    def to_ranges(self):
        return [(span.start, span.end) for span in self]

    @classmethod
    def from_ranges(cls, ranges_list, pattern_creator=None, pattern=None, is_param=False):
        spans = SpanList(
            [
                Span(
                    start,
                    end,
                    pattern_creator=pattern_creator,
                    pattern=pattern,
                    is_param=is_param
                ) for start, end in ranges_list
            ]
        )  # yapf: disable
        return spans

    @classmethod
    def not_overlapping_spans(cls, sorted_spans):
        """
        For given list of spans, returns list of non-overlapping spans.
        Greedy, takes spans one after another from sorted list and tries to add it into non_overlapping spans.
        :param [Span] sorted_spans: sorted spans due to some order
        """
        spans_not_overlapping = SpanList()
        for span in sorted_spans:
            not_overlaps = True
            for good_span in spans_not_overlapping:
                if span.overlaps(good_span):
                    not_overlaps = False
                    break
            if not_overlaps:
                spans_not_overlapping.append(span)
        return spans_not_overlapping.sort_by_start_and_end()

    def complementary_spans(self, start_index, end_index, pattern_creator):
        ranges = self.to_ranges()
        complement_ranges = complementary_ranges(ranges, start_index, end_index)
        return self.from_ranges(complement_ranges, pattern_creator=pattern_creator)

    def overlapping_check(self):
        if not self:
            return
        sorted_spans = self.sort_by_start_and_end()
        previous_span = sorted_spans[0]
        for span in sorted_spans[1:]:
            if previous_span.overlaps(span):
                raise OverlappingSpansError(previous_span, span)
            previous_span = span
