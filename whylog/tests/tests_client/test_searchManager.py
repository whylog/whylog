from unittest import TestCase

from whylog.config.mocked_investigation_plan import *
from whylog.log_reader import SearchManager


class TestBasic(TestCase):
    def test_searchManager_creation(self):
        investigation_plan = mocked_investigation_plan()
        manager = SearchManager(investigation_plan)
        assert isinstance(manager, SearchManager)
