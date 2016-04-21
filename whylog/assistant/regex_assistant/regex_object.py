from whylog.assistant.regex_assistant.regex import (
    create_obvious_regex, group_spans_from_regex, regex_from_group_spans, verify_regex
)
from whylog.assistant.span_list import SpanList


class RegexObject(object):
    """
    Container for information about line and corresponding regex
    Supports interactive updates like adding/removing groups to regex, replacing regex
    Keeps own data integrity - especially consistency between regex and groups (group_spans).
    Verifies updates.
    Not responsible for guessing where are groups in regex
    """

    def __init__(self, line_object):
        """
        :param FrontInput line_object: object that represents line
        :param line_text: line text (raw string)
        :param regex: regex corresponding to line_text
        :param [Span] group_spans: represents regex groups, not overlapping each other
        """
        self.line = line_object
        self.line_text = line_object.line_content
        self.group_spans = SpanList()
        self.regex = self._update_regex()

    def _update_regex(self):
        """
        Builds regex from spans
        """
        return regex_from_group_spans(self.group_spans, self.line_text)

    def update_forcefully(self, new_spans):
        """
        Completely replaces group_spans to new_spans, updates regex
        :param new_spans: non-overlapping spans (if they overlaps error will be raised)
        """
        # TODO: check if new_spans don't intersect
        self.group_spans = new_spans
        self.regex = regex_from_group_spans(self.group_spans, self.line_text)

    def update(self, spans_to_add, spans_to_remove):
        raise NotImplementedError

    def replace_regex(self, new_regex):
        """
        Assigns self.regex to new_regex.

        Throws NotMatchingRegexError if new_regex doesn't match self.line_text
        If needed, improves new_regex: new_regex = '^' + new_regex + '$' (regex must match whole line)
        Updates self.group_spans so that they correspond to new_regex groups
        """

        verify_regex(new_regex, self.line_text)

        if not new_regex[0] == '^':
            new_regex = '^' + new_regex
        if not new_regex[-1] == '$':
            new_regex += '$'

        self.group_spans = group_spans_from_regex(new_regex, self.line_text)
        self.regex = new_regex

    def verify(self):
        """
        Verifies properties such as:
        - regex matching a whole text
        - regex matching text in a one way only
        - group_spans converters (Span.converter) are proper
        If properties are not met, proper exceptions are returned.
        """
        return NotImplementedError
