from whylog.exceptions import WhylogError


class UnsupportedConverterError(WhylogError):
    def __init__(self, converter_class_name):
        self.converter_class_name = converter_class_name

    def __str__(self):
        return 'This whylog version do not handle %s. Please upgrade Whylog' % self.converter_class_name


class ConverterError(WhylogError):
    def __init__(self, converting_param):
        self.converting_param = converting_param

    def __str__(self):
        return 'Cannot convert %s' % (self.converting_param,)