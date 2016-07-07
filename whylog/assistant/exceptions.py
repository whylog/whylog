from whylog.exceptions import WhylogError


class WhylogAssistantError(WhylogError):
    pass


class NotMatchingPatternError(WhylogAssistantError):
    pass


class DateFromFutureError(WhylogAssistantError):
    def __init__(self, parsed_date, date_text):
        super(DateFromFutureError, self).__init__()
        self.date_text = date_text
        self.parsed_date = parsed_date

    def __str__(self):
        return 'Date is from future, date text: %s parsed date: %s' % (
            self.date_text, self.parsed_date
        )


class NoDateGroupError(WhylogAssistantError):
    def __init__(self, line_content, regex, line_index):
        super(NoDateGroupError, self).__init__()
        self.line_content = line_content
        self.regex = regex
        self.line_index = line_index

    def __str__(self):
        return 'No date group in regex, regex: %s line content: %s' % (
            self.regex, self.line_content
        )


class UnsupportedAssistantError(WhylogAssistantError):
    def __init__(self, assistant_class_name):
        super(UnsupportedAssistantError, self).__init__()
        self.assistant_class_name = assistant_class_name

    def __str__(self):
        return 'This whylog version do not handle %s. Please upgrade Whylog' % self.assistant_class_name


class SpanConstructorParamsError(WhylogError):
    def __init__(self, start, end):
        super(SpanConstructorParamsError, self).__init__()
        self.start = start
        self.end = end

    def __str__(self):
        return 'Wrong Span constructor params. Should be: %s < %s' % (self.start, self.end)


class UnableToCreatePatternError(WhylogError):
    def __init__(self, start, end):
        super(UnableToCreatePatternError, self).__init__()
        self.start = start
        self.end = end

    def __str__(self):
        return 'No pattern or pattern creator in Span constructor for span in (%s, %s)' % \
               (self.start, self.end)
