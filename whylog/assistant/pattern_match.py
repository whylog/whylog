from collections import namedtuple


class ParamGroup(object):
    def __init__(self, content, converter):
        self.content = content
        self.converter = converter

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

# :type param_groups: dict[int, ParamGroup]
PatternMatch = namedtuple('PatternMatch', ['line_text', 'pattern', 'param_groups'])
