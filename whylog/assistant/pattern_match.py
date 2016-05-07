from collections import namedtuple

ParamGroup = namedtuple('ParamGroup', ['content', 'converter'])


class PatternMatch(object):
    """
    :type param_groups: dict[int, ParamGroup]
    """

    def __init__(self, line_text, pattern, param_groups):
        self.line_text = line_text
        self.pattern = pattern
        self.param_groups = param_groups
