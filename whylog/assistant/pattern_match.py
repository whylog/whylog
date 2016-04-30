from collections import namedtuple

ParamGroup = namedtuple('ParamGroup', ['content', 'converter'])

PatternMatch = namedtuple('PatternMatch', ['line_text', 'pattern', 'param_groups'])

