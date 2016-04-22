class ParamGroup(object):
    def __init__(self, content, converter):
        self.content = content
        self.converter = converter


class PatternObject(object):
    def __init__(self, line_text, pattern, param_groups):
        self.line_text = line_text
        self.pattern = pattern
        self.param_groups = param_groups
