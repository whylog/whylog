class UserParserIntent(object):
    def __init__(self, log_type_name, regex, primary_key_groups, data_conversions=None):
        self.log_type_name = log_type_name
        self.regex = regex
        self.primary_key_groups = primary_key_groups
        self.data_conversions = data_conversions or {}


class UserConstraintIntent(object):
    def __init__(self, constr_type, groups, params=None):
        self.type = constr_type
        self.groups = groups
        self.params = params or {}


class UserRuleIntent(object):
    def __init__(self, parsers, effect_id, constraints):
        self.parsers = parsers
        self.effect_id = effect_id
        self.constraints = constraints
