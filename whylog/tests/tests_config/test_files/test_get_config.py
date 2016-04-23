from unittest import TestCase

import os

from whylog.config import ConfigFactory


class TestBasic(TestCase):
    def test_no_config_file_found(self):
        assert ConfigFactory._find_path_to_config() is None
        assert False
