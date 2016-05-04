import re

import six

from whylog.assistant.pattern_match import ParamGroup, PatternMatch
from whylog.assistant.regex_assistant.regex import (
    create_obvious_regex, regex_from_group_spans, verify_regex
)
from whylog.assistant.spans_finding import find_date_spans


def guess_pattern_match(text):
    pattern_match_with_dates = guess_pattern_match_with_dates(text)
    obvious_pattern_match = guess_obvious_pattern_match(text)
    #TODO: following list will be longer if we guess more regexes.
    return [pattern_match_with_dates, obvious_pattern_match]


def guess_pattern_match_with_dates(text):
    group_spans = find_date_spans(text)
    regex = regex_from_group_spans(group_spans, text)
    groups = _groups_from_spans(group_spans, regex, text)
    return PatternMatch(text, regex, groups)


def guess_obvious_pattern_match(text):
    regex = create_obvious_regex(text)
    return PatternMatch(text, regex, list())


def _groups_from_spans(spans, regex, text):
    verify_regex(regex, text)
    matcher = re.match(re.compile(regex), text)
    group_contents = matcher.groups()
    sorted_spans = spans.sort_by_start_and_end()
    group_converters = [span.data_type for span in sorted_spans]
    groups = [
        ParamGroup(content, converter)
        for content, converter in six.moves.zip(group_contents, group_converters)
    ]
    groups_dict = dict((key + 1, groups[key]) for key in six.moves.range(len(groups)))
    return groups_dict
