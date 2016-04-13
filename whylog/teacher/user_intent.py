class Group(object):
    def __init__(self, group_content, group_converter):
        self.content = group_content
        self.converter = group_converter


class UserParserIntent(object):
    def __init__(
        self, pattern_type, pattern_name, pattern, log_type_name, primary_key_groups, groups, line_content,
        line_offset, line_resource_location
    ):
        self.pattern_type = self.pattern_type
        self.pattern_name = pattern_name
        self.pattern = pattern
        self.log_type_name = log_type_name
        self.primary_key_groups = primary_key_groups
        self.groups = groups  # {group_id : Group}
        self.line_content = line_content
        self.line_offset = line_offset
        self.line_resource_location = line_resource_location


class UserConstraintIntent(object):
    def __init__(self, constr_type, groups, params=None):
        self.type = constr_type
        self.groups = groups
        self.params = params or {}


class UserRuleIntent(object):
    def __init__(self, effect_id, parsers=None, constraints=None):
        self.effect_id = effect_id
        self.parsers = parsers or {}
        self.constraints = constraints or []
