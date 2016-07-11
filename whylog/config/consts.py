from whylog.config.filename_matchers import WildCardFilenameMatcher
from whylog.config.log_type import LogType
from whylog.config.super_parser import RegexSuperParser

EFFECT_NUMBER = 0

DEFAULT_NAME = "default"
DEFAULT_MATCHER = WildCardFilenameMatcher(
    "localhost", "", DEFAULT_NAME, RegexSuperParser("", [], {})
)
DEFAULT_LOG_TYPE = LogType(
    DEFAULT_NAME, [DEFAULT_MATCHER]
) # yapf: disable


class YamlFileNames(object):
    rules = 'rules.yaml'
    parsers = 'parsers.yaml'
    default_log_types = 'log_types.yaml'
    unix_log_types = 'unix_log_types.yaml'
    windows_log_types = 'windows_log_types.yaml'
    settings = 'settings.yaml'
