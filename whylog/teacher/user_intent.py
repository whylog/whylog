class LineParamGroup(object):
    def __init__(self, param_content, param_converter):
        self.content = param_content
        self.converter = param_converter


class UserParserIntent(object):
    def __init__(
        self, pattern_type, pattern_name, pattern, log_type_name, primary_key_groups, groups,
        line_content, line_offset, line_resource_location
    ):
        self.pattern_type = pattern_type
        self.pattern_name = pattern_name
        self.pattern = pattern
        self.log_type_name = log_type_name
        self.primary_key_groups = primary_key_groups
        self.groups = groups  # {group_id : LineParamGroup}
        self.line_content = line_content
        self.line_offset = line_offset
        self.line_resource_location = line_resource_location
        self.id = parser_id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class UserConstraintIntent(object):
    def __init__(self, constr_type, groups, params=None, constraint_id=None):
        self.type = constr_type
        self.groups = groups
        self.params = params or {}
        self.id = constraint_id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class UserRuleIntent(object):
    def __init__(self, effect_id, parsers=None, constraints=None):
        self.effect_id = effect_id
        self.parsers = parsers or {}
        self.constraints = constraints or []
