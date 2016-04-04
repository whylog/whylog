"""
Methods responsible for finding spans (potential params) for given text.
Some heuristic included.
"""

import re
from datetime import datetime

from dateutil.parser import parse as date_parse

from whylog.assistant.const import DataType, DateParams
from whylog.assistant.regex_assistant.regex import create_date_regex
from whylog.assistant.span import Span, not_overlapping_spans, sort_as_date


def find_date_spans(text, regexes=None):
    regexes = regexes or {}

    forced_date_spans = _find_date_spans_by_force(text)
    regex_date_spans = _find_date_spans_by_regex(regexes, text)

    unique_spans = forced_date_spans.union(regex_date_spans)

    ordered_date_spans = sort_as_date(unique_spans)

    best_spans = not_overlapping_spans(ordered_date_spans)

    return best_spans


def _find_date_spans_by_regex(regexes, text):
    return _find_spans_by_regex(
        regexes,
        text,
        pattern_creator=create_date_regex,
        converter=DataType.DATE
    )


def _find_date_spans_by_force(text):
    date_spans = set()

    proper_starts, proper_ends = _possible_span_starts_and_ends(text)
    proper_ends.reverse()

    date_now = datetime.now()
    not_overlapping_start = 0
    for start in proper_starts:
        if start < not_overlapping_start:
            continue
        for end in proper_ends:
            if end < start + DateParams.MIN_DATE_LENGTH:
                break
            try:
                date_text = text[start:end]
                date = date_parse(date_text)
            except (ValueError):
                continue

            if date_now.year - date.year < -1:
                continue
            new_span = Span(start, end, pattern_creator=create_date_regex, data_type=DataType.DATE)
            date_spans.add(new_span)
            not_overlapping_start = end
            # break, because we don't care about shorter date groups
            break
    return date_spans


def _find_spans_by_regex(regexes, text, pattern_creator=None, converter=DataType.STRING):
    spans = set()
    for compiled_regex, regex in regexes.items():
        for match in re.finditer(compiled_regex, text):
            new_span = Span(match.start(0), match.end(0), regex, pattern_creator, converter)
            spans.add(new_span)
    return spans


def _possible_span_starts_and_ends(text):
    """
    for given text finds possible starts and ends of potential spans.

    Based on observation that group does not start/end in the middle of alphanumerical sequence
    or whitespace sequence and is not position of punctuation mark

    I.e For given text: "[18/Sep/2007] Reboot failed",
    possible starts are: '1', 'S', '2', 'R', 'f',
    possible ends are: '8', 'p', '7', 't', 'd'
    """

    starts = []
    start_pattern = re.compile(r"(?<=[^\w])[\w]|^[\w]")
    for match in re.finditer(start_pattern, text):
        starts.append(match.start(0))
    ends = []
    end_pattern = re.compile(r"\w(?=[^\w])|\w$")
    for match in re.finditer(end_pattern, text):
        ends.append(match.end(0))
    return starts, ends
