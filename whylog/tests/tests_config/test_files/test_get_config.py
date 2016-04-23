import os

from unittest import TestCase


from whylog.config import ConfigFactory


class TestBasic(TestCase):
    def test_search_in_parents_directories(self):
        current_path = os.getcwd()
        print ConfigFactory._create_new_config_dir()
        # os.chdir(current_path)