from unittest import TestCase
from os.path import join

from whylog.config import YamlConfig

path_test_files = ['whylog', 'tests', 'tests_config', 'test_files']


class TestConfig(TestCase):
    def test_parsers_loading(self):
        path = join(*path_test_files)
        parsers_path = join(path, 'parsers.yaml')
        rules_path = join(path, 'rules.yaml')
        log_location_path = join(path, 'log_locations.yaml')

        config = YamlConfig(
            parsers_path=parsers_path,
            rules_path=rules_path,
            log_locations_path=log_location_path,
        )

        assert len(config._parsers) == 4
        assert sorted(parser._name
                      for parser in config._parsers) == ['cause', 'effect', 'intermediate', 'other']
        regex_parser = filter(lambda parser: parser.__class__.__name__ == "RegexParser",
                              config._parsers)
        assert len(regex_parser) == 3
        assert sorted(map(lambda x: x._name, regex_parser)) == ['cause', 'effect', 'intermediate']
        wildcards_parsers = filter(lambda parser: parser.__class__.__name__ == "WildCardParser",
                                   config._parsers)
        assert len(wildcards_parsers) == 1
        assert map(lambda x: x._name, wildcards_parsers) == ['other']
