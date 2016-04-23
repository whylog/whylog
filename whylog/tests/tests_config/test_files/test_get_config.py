import os

from unittest import TestCase


from whylog.config import ConfigFactory


class TestBasic(TestCase):
    def test_search_in_parents_directories(self):
        current_path = os.getcwd()
        path = ConfigFactory._search_in_parents_directories()
        print path
        os.chdir(current_path)