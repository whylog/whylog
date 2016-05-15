from whylog.exceptions import WhylogError


class TeacherError(WhylogError):
    pass


class NotUniqueParserName(TeacherError):
    def __init__(self, parser_name):
        self.parser_name = parser_name

    def __str__(self):
        return 'Name is not unique, name: %s' % (self.parser_name,)
