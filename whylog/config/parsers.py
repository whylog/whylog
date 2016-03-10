import re
import uuid
from abc import ABCMeta, abstractmethod
import six


@six.add_metaclass(ABCMeta)
class AbstractParser(object):
    @abstractmethod
    def get_clue(self, line):
        pass


class RegexParser(AbstractParser):
    def __init__(self, name, regex, primary_key_groups, log_type, convertions):
        self.name = name
        self.regex_str = regex
        self.regex = re.compile(regex)
        self.primary_key_groups = primary_key_groups
        self.log_type = log_type
        self.convertions = convertions

    def get_clue(self, line):
        pass

    def to_data_access_object_form(self):
        return RegexParserDAO(
            self.name, self.regex_str, self.primary_key_groups, self.log_type, self.convertions
        )


class RegexParserDAO(object):
    def __init__(self, name, regex, primary_key_groups, log_type, convertions):
        self.name = name
        self.regex_str = regex
        self.primary_key_groups = primary_key_groups
        self.log_type = log_type
        self.convertions = convertions

    def create_parser(self):
        return RegexParser(
            self.name, self.regex_str, self.primary_key_groups, self.log_type, self.convertions
        )


@six.add_metaclass(ABCMeta)
class AbstractParserFactory(object):
    @classmethod
    @abstractmethod
    def create_from_intent(cls, parser_intent):
        pass


class RegexParserFactory(object):
    @classmethod
    def create_from_intent(cls, parser_intent):
        return RegexParser(
            str(uuid.uuid4()), parser_intent.regex, parser_intent.primary_key_groups,
            parser_intent.log_type_name, parser_intent.data_conversions
        )
