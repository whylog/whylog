class ParamGroup(object):
    def __init__(self, content, converter):
        self.content = content
        self.converter = converter

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class PatternMatch(object):
    def __init__(self, line_text, pattern, param_groups, primary_key=None):
        # :type param_groups: dict[int, ParamGroup]
        self.line_text = line_text
        self.pattern = pattern
        self.param_groups = param_groups
        self.primary_key = primary_key
        if primary_key is None:
            if not self.param_groups:
                self.primary_key = []
            else:
                self.primary_key = [min(self.param_groups.keys())]
