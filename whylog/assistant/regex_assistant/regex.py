"""
Regex verification and creating (but not finding groups in regex)
"""
import re

special_characters = frozenset(['.', '^', '$', '*', '+', '{', '}', '?', '[', ']', '|', '(', ')'])


class NoDateGroupError(Exception):
    def __init__(self, line_content, regex, line_index):
        self.line_content = line_content
        self.regex = regex
        self.line_index = line_index

    def __str__(self):
        return 'No date group in regex. Regex: %s. Line content: %s' % (
            self.regex, self.line_content
        )


class NotMatchingRegexError(Exception):
    def __init__(self, line_content, regex):
        self.line_content = line_content
        self.regex = regex

    def __str__(self):
        return 'Regex do not match line. Regex: %s. Line content: %s' % (
            self.regex, self.line_content
        )


class DateFromFutureError(Exception):
    def __init__(self, parsed_date, date_text):
        self.date_text = date_text
        self.parsed_date = parsed_date

    def __str__(self):
        return 'Date is from future. date text %s,  parsed date %s' % (
            self.date_text, self.parsed_date
        )


def verify_regex(regex, text):
    """
    Verifies regex properties such as:
    - matching a whole text
    - matching text in a one way only
    If properties are not met, proper exceptions are returned.
    """
    # TODO: verify if regex matches text in a one way only

    # regex must match a whole text from its beginning to end.
    if not regex[0] == "^":
        regex = "^" + regex
    if not regex[-1] == "$":
        regex += "$"
    pattern = re.compile(regex)

    m = re.search(pattern, text)
    matched = False
    groups = []
    errors = []
    if m is not None:
        matched = True
        groups = m.groups()
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
    for c in double_backslashed_text:
        if c in special_characters:
            regex += "\\"
        regex += c
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
    group_regex = r"[a-zA-Z]+|[0-9]+|\s+|[\W]+"
    group_pattern = re.compile(group_regex)
    date_regex = r""
    for match in re.finditer(group_pattern, date_text):
        c = date_text[match.start(0)]
        if c.isalpha():
            date_regex += "[a-zA-Z]+"
        elif c.isdigit():
            length = match.end(0) - match.start(0)
            repet = "+"
            if length <= 2:
                repet = "{1,2}"
            elif length == 4:
                repet = "{4}"
            date_regex += "[0-9]" + repet
        else:
            date_regex += create_obvious_regex(match.group(0))
    return date_regex


def create_silly_regex(date_text):
    return r".*"
