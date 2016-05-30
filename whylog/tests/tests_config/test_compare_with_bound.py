from datetime import datetime
from unittest import TestCase

from whylog.config.investigation_plan import InvestigationStep
from whylog.config.utils import CompareResult


class TestBoundCompare(TestCase):
    @classmethod
    def setUp(cls):
        search_ranges = {
            'date': {
                InvestigationStep.LEFT_BOUND: datetime(2015, 12, 3, 12, 8, 0),
                InvestigationStep.RIGHT_BOUND: datetime(2015, 12, 3, 12, 8, 11)
            }
        }  # yapf: disable
        cls.investigation_step = InvestigationStep(None, search_ranges)

    def test_existing_bounds_in_investigation_step(self):
        super_parser_groups = [('date', datetime(2015, 12, 3, 12, 8, 9))]
        assert self.investigation_step.compare_with_bound(
            InvestigationStep.LEFT_BOUND, super_parser_groups
        ) == CompareResult.GT
        assert self.investigation_step.compare_with_bound(
            InvestigationStep.RIGHT_BOUND, super_parser_groups
        ) == CompareResult.LT

        super_parser_groups = [('date', datetime(2015, 12, 3, 12, 8, 0))]
        assert self.investigation_step.compare_with_bound(
            InvestigationStep.LEFT_BOUND, super_parser_groups
        ) == CompareResult.EQ

    def test_no_existing_bounds_in_invesitgation_step(self):
        super_parser_groups = [('int', 1)]
        assert self.investigation_step.compare_with_bound(
            InvestigationStep.LEFT_BOUND, super_parser_groups
        ) == CompareResult.LT
        assert self.investigation_step.compare_with_bound(
            InvestigationStep.RIGHT_BOUND, super_parser_groups
        ) == CompareResult.GT

    def test_empty_super_parser_groups(self):
        assert self.investigation_step.compare_with_bound(InvestigationStep.LEFT_BOUND, []
                                                         ) == CompareResult.LT
        assert self.investigation_step.compare_with_bound(InvestigationStep.RIGHT_BOUND, []
                                                         ) == CompareResult.GT
