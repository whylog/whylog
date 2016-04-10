"""
Regex verification and creating (but not finding groups in regex)
"""

import re

from whylog.assistant.regex_assistant.exceptions import NotMatchingRegexError

special_characters = frozenset('.^$*+{}?[]|()]')
group_pattern = re.compile(r"[a-zA-Z]+|[0-9]+|\s+|[\W]+")


def verify_regex(regex, text):
    """
    Verifies regex properties such as:
    - matching a whole text
    If properties are not met, exception is raised.
    """

    # regex must match a whole text from its beginning to end.
    matcher = re.match('^%s$' % (regex,), text)

    if matcher is None:
        raise NotMatchingRegexError(text, regex)
    else:
        return matcher.groups()


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
    date_regex = r""
    for matcher in group_pattern.finditer(date_text):
        start, end = matcher.span(0)
        char = date_text[start]
        if char.isalpha():
            date_regex += "[a-zA-Z]+"
        elif char.isdigit():
            length = matcher.end(0) - matcher.start(0)
            repetition_count = "+"
            if length <= 2:
                repetition_count = "{1,2}"
            elif length == 4:
                repetition_count = "{4}"
            date_regex += "[0-9]" + repetition_count
        else:
            date_regex += create_obvious_regex(matcher.group(0))
    return date_regex


def create_matching_everything_regex(date_text):
    return r".*"
