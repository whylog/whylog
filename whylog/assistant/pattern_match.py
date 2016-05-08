from collections import namedtuple

ParamGroup = namedtuple('ParamGroup', ['content', 'converter'])

# :type param_groups: dict[int, ParamGroup]
PatternMatch = namedtuple('PatternMatch', ['line_text', 'pattern', 'param_groups'])
