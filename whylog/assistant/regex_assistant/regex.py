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
            len = match.end(0) - match.start(0)
            repet = "+"
            if len <= 2:
                repet = "{1,2}"
            elif len == 4:
                repet = "{4}"
            date_regex += "[0-9]" + repet
        else:
            date_regex += create_obvious_regex(match.group(0))
    return date_regex


def create_silly_regex(date_text):
    return r".*"
