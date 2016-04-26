from whylog.exceptions import WhylogError


class WhylogConfigError(WhylogError):
    pass


class UnsupportedFilenameMatcher(WhylogConfigError):
    def __init__(self, matcher_class_name):
        self.matcher_class_name = matcher_class_name

    def __str__(self):
        return 'This whylog version do not handle %s. Please upgrade Whylog' % self.matcher_class_name


class UnsupportedConfigType(WhylogConfigError):
    def __init__(self, unsupported_type):
        self.unsupported_type = unsupported_type

    def __str__(self):
        return 'This whylog version do not handle %s. Please upgrade Whylog' % self.unsupported_type
