"""
Span as representation of interval and its pattern in som text
Auxilary methods for Span
"""

from operator import attrgetter

from whylog.assistant.const import DataType


class OverlappingSpansError(Exception):
    def __init__(self, span1, span2):
        self.span1 = span1
        self.span2 = span2

    def __str__(self):
        return "%s overlaps %s" % (self.span1, self.span2)


class SpanConstructorParamsError(Exception):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return 'Wrong Span constructor params. Should be: %s < %s' % (self.start, self.end)


class UnableToCreatePatternError(Exception):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return 'No pattern or pattern creator in Span constructor for span in (%s, %s)' % \
               (self.start, self.end)


class Span(object):
    """
    Represents interval in some text and corresponding to it pattern

    Spans are "bricks" from which we build text (log) pattern.
    Span can represent parameter and const fragment of text.
    I.e. for log: "18/Sep/1994 12:34:15 error occurred on machine comp42 while rebooting",
    parameters could be: "18/Sep/1994 12:34:15" and "comp42"
    then const fragments will be: " error occurred on machine ", " while rebooting"

    Span keeps some specific information that are useful in params representation:
    - data_type - type of data in interval represented by Span.
    I.e Span representing "18/Sep/1994 12:34:15" has data_type DATE
    """

    def __init__(
        self,
        start,
        end,
        pattern_creator=None,
        is_param=True,
        pattern=None,
        data_type=DataType.STRING
    ):
        """
        :param start, end: represent interval [start, end) of some text
        :param is_param: True if Span represents parameter in some text, False otherwise
        :param pattern: pattern corresponding to this interval in some text (i.e. regex)
        :param pattern_creator: function that creates pattern for given interval and text
        :param data_type: type of data represented by interval in text.
        """
        if start >= end:
            raise SpanConstructorParamsError(start, end)
        self.start = start
        self.end = end
        # length is needed many times for sorting, so counted here once.
        self.length = end - start
        self.is_param = is_param
        # pattern or pattern_creator must be defined
        if not (pattern or pattern_creator):
            raise UnableToCreatePatternError(start, end)
        self.pattern = pattern
        self.pattern_creator = pattern_creator
        self.data_type = data_type

    def __repr__(self):
        return "Span(" + str(self.start) + ", " + str(self.end) + ")"

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(tuple(self.__dict__.values()))

    def overlaps(self, other):
        return not (other.end <= self.start or other.start > self.start)

    def update_pattern(self, text, force=False):
        span_text = text[self.start:self.end]
        if not self.pattern_creator:
            return
        if force:
            self.pattern = self.pattern_creator(span_text)
        else:
            self.pattern = self.pattern or self.pattern_creator(span_text)


def update_span_patterns(spans, text):
    for span in spans:
        span.update_pattern(text)
    return spans


def sort_by_start(spans):
    return sorted(spans, key=attrgetter('start'))


def sort_as_date(spans):
    # we prefer longer dates, because it is safer (date is different in each log)
    return sorted(spans, key=attrgetter('length'), reverse=True)


def complementary_intervals(spans, start_index, end_index):
    overlapping_check(spans)
    compl_pairs = set()
    sorted_spans = sort_by_start(spans)
    span_start = start_index
    for span in sorted_spans:
        span_end = span.start
        if span_start < span_end:
            compl_pairs.add((span_start, span_end))
        span_start = span.end
    if span_start < end_index:
        compl_pairs.add((span_start, end_index))
    return list(compl_pairs)


def spans_from_pairs(pairs, pattern_creator=None, pattern=None, is_param=False):
    spans = [
        Span(
            pair[0],
            pair[1],
            pattern_creator=pattern_creator,
            pattern=pattern,
            is_param=is_param
        ) for pair in pairs
    ]
    overlapping_check(spans)
    return list(spans)


def overlapping_check(spans):
    if len(spans) == 0:
        return
    sorted_spans = sort_by_start(spans)
    last_span = sorted_spans[0]
    for span in sorted_spans[1:]:
        if last_span.overlaps(span):
            raise OverlappingSpansError(last_span, span)
        last_span = span


def not_overlapping_spans(sorted_spans):
    """
    For given list of spans, returns list of non-overlapping spans.
    Greedy, takes spans one after another from sorted list and tries to add it into non_overlapping spans.
    :param [Span] sorted_spans: sorted spans due to some order
    """
    spans_not_overlapping = []
    for span in sorted_spans:
        not_overlaps = True
        for good_span in spans_not_overlapping:
            if span.overlaps(good_span):
                not_overlaps = False
                break
        if not_overlaps:
            spans_not_overlapping.append(span)
    return sort_by_start(spans_not_overlapping)
