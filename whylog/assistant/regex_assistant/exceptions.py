from whylog.assistant.exceptions import WhylogAssistantError


class WhylogRegexAssistantError(WhylogAssistantError):
    pass


class NotMatchingRegexError(WhylogRegexAssistantError):
    def __init__(self, line_content, regex):
        self.line_content = line_content
        self.regex = regex

    def __str__(self):
        return 'Regex does not match line, regex: %s line content: %s' % (
            self.regex, self.line_content
        )
