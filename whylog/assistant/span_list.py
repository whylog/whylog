from operator import attrgetter
from whylog.assistant.span import Span
from whylog.exceptions import WhylogError


class OverlappingSpansError(WhylogError):
    def __init__(self, span1, span2):
        self.span1 = span1
        self.span2 = span2

    def __str__(self):
        return "%s overlaps %s" % (self.span1, self.span2)


class SpanList(list):
    def __add__(self, other):
        return SpanList(super(SpanList, self).__add__(other))

    def sort_by_start(self):
        return SpanList(sorted(self, key=attrgetter('start')))

    def sort_reversed_by_length(self):
        # we prefer longer dates, because it is safer (date is different in each log)
        return SpanList(sorted(self, key=attrgetter('length'), reverse=True))

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
        )
        cls.overlapping_check(spans)
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
        return spans_not_overlapping.sort_by_start()

    def complementary_intervals(self, start_index, end_index):
        self.overlapping_check()
        compl_intervals = set()
        span_start = start_index
        for span in self.sort_by_start():
            new_span_end = span.start
            if span_start < new_span_end:
                compl_intervals.add((span_start, new_span_end))
            span_start = span.end
        if span_start < end_index:
            compl_intervals.add((span_start, end_index))
        return compl_intervals

    def overlapping_check(self):
        if not self:
            return
        sorted_spans = self.sort_by_start()
        previous_span = sorted_spans[0]
        for span in sorted_spans[1:]:
            if previous_span.overlaps(span):
                raise OverlappingSpansError(previous_span, span)
            previous_span = span
