from whylog.exceptions import WhylogError


class TeacherError(WhylogError):
    pass


class NotUniqueParserName(TeacherError):
    def __init__(self, parser_name):
        self.parser_name = parser_name

    def __str__(self):
        return 'Name is not unique, name: %s' % (self.parser_name,)


class TeacherWarning(object):
    pass


class NotMatchingPatternWarning(TeacherWarning):
    def __init__(self, line, pattern):
        self.line = line
        self.pattern = pattern

    def __str__(self):
        return 'Pattern does not match line, pattern: %s, line: %s' % (self.pattern, self.line)
