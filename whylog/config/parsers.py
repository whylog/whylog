from abc import ABCMeta, abstractmethod

import uuid


class AbstractParser(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_clue(self, line):
        pass


class RegexParser(AbstractParser):
    def __init__(self, name, regex, primary_key_groups, log_type, convertions):
        self.name = name
        self.regex_str = regex
        self.primary_key_groups = primary_key_groups
        self.log_type = log_type
        self.convertions = convertions

    def get_clue(self, line):
        pass


class RegexParserFactory(object):
    @classmethod
    def create_from_intent(cls, parser_intent):
        return RegexParser(
            str(uuid.uuid4()), parser_intent.regex, parser_intent.primary_key_groups,
            parser_intent.log_type_name, parser_intent.data_conversions
        )
