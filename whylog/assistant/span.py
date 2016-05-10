"""
Span as representation of interval and its pattern in som text
Auxilary methods for Span
"""
import six

from whylog.assistant.const import ConverterType
from whylog.exceptions import WhylogError


class SpanConstructorParamsError(WhylogError):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return 'Wrong Span constructor params. Should be: %s < %s' % (self.start, self.end)


class UnableToCreatePatternError(WhylogError):
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
        converter=ConverterType.TO_STRING
    ):
        """
        :param start, end: represent interval [start, end) of some text
        :param is_param: True if Span represents parameter in some text, False otherwise
        :param pattern: pattern corresponding to this interval in some text (i.e. regex)
        :param pattern_creator: function that creates pattern for given interval and text
        :param converter: type of data represented by interval in text.
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
        self.converter = converter

    def __repr__(self):
        return "Span(" + str(self.start) + ", " + str(self.end) + ")"

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(tuple(six.itervalues(self.__dict__)))

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
