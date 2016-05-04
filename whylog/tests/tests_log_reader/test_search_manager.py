from unittest import TestCase

from whylog.config.mocked_investigation_plan import mocked_investigation_plan
from whylog.log_reader import SearchManager


class TestBasic(TestCase):
    def test_search_manager_creation(self):
        investigation_plan = mocked_investigation_plan()
        manager = SearchManager(investigation_plan)
        assert isinstance(manager, SearchManager)
