"""
Regex verification and creating (but not finding groups in regex)
"""

import re

from whylog.assistant.regex_assistant.exceptions import NotMatchingRegexError

special_characters = frozenset('.^$*+{}?[]|()]')


def verify_regex(regex, text):
    """
    Verifies regex properties such as:
    - matching a whole text
    - matching text in a one way only
    If properties are not met, proper exceptions are returned.
    """
    # TODO: verify if regex matches text in a one way only

    # regex must match a whole text from its beginning to end.
    whole_text_regex = "^" + regex + "$"
    pattern = re.compile(whole_text_regex)

    match = re.match(pattern, text)
    matched = False
    groups = []
    errors = []
    if match is not None:
        matched = True
        groups = match.groups()
    else:
        errors.append(NotMatchingRegexError(text, regex))
    return matched, groups, errors


def create_obvious_regex(text):
    """
    Creates regex form text by simple transformation:
    - backslash before backslash
    - backslash before special character
    :param text: must be a raw string
    :return: obvious regex
    """
    double_backslashed_text = text.replace("\\", "\\\\")
    regex = r""
    for char in double_backslashed_text:
        if char in special_characters:
            regex += "\\"
        regex += char
    return regex


def create_date_regex(date_text):
    """
    Creates date regex based on observation that numbers in date
    are represented as 1, 2 or 4 -digit numbers
    i.e guess_date_regex("23/March/2016") = [0-9]{1,2}/[a-zA-Z]+/[0-9]{4}
    :param date_text: must be a raw string
    :return: date regex
    """
    # We divide date_text into groups consisting of:
    # only alpha or only num or only non-alphanumerical marks
    group_regex = re.compile(r"[a-zA-Z]+|[0-9]+|\s+|[\W]+")
    date_regex = r""
    for matcher in re.finditer(group_regex, date_text):
        start, end = matcher.span(0)
        char = date_text[start]
        if char.isalpha():
            date_regex += "[a-zA-Z]+"
        elif char.isdigit():
            length = matcher.end(0) - matcher.start(0)
            repetition_cnt = "+"
            if length <= 2:
                repetition_cnt = "{1,2}"
            elif length == 4:
                repetition_cnt = "{4}"
            date_regex += "[0-9]" + repetition_cnt
        else:
            date_regex += create_obvious_regex(matcher.group(0))
    return date_regex


def create_silly_regex(date_text):
    return r".*"
