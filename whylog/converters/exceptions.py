from whylog.exceptions import WhylogError


class UnsupportedConverter(WhylogError):
    def __init__(self, converter_class_name):
        self.converter_class_name = converter_class_name

    def __str__(self):
        return 'This whylog version do not handle %s. Please upgrade Whylog' % self.converter_class_name
