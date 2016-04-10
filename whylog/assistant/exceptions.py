from whylog.exceptions import WhylogError


class WhylogAssistantError(WhylogError):
    pass


class DateFromFutureError(WhylogAssistantError):
    def __init__(self, parsed_date, date_text):
        self.date_text = date_text
        self.parsed_date = parsed_date

    def __str__(self):
        return 'Date is from future, date text: %s parsed date: %s' % (
            self.date_text, self.parsed_date
        )


class NoDateGroupError(WhylogAssistantError):
    def __init__(self, line_content, regex, line_index):
        self.line_content = line_content
        self.regex = regex
        self.line_index = line_index

    def __str__(self):
        return 'No date group in regex, regex: %s line content: %s' % (
            self.regex, self.line_content
        )
