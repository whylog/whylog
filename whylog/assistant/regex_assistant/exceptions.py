from whylog.assistant.exceptions import NotMatchingPatternError


class NotMatchingRegexError(NotMatchingPatternError):
    def __init__(self, line_content, regex):
        super(NotMatchingRegexError, self).__init__()
        self.line_content = line_content
        self.regex = regex

    def __str__(self):
        return 'Regex does not match line, regex: %s line content: %s' % (
            self.regex, self.line_content
        )
