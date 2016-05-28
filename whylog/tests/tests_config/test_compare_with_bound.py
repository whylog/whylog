from datetime import datetime
from unittest import TestCase

from whylog.config.investigation_plan import InvestigationStep
from whylog.config.utils import CompareResult


class TestBoundCompare(TestCase):
    def test_compare_with_bound(self):
        search_ranges = {
            'date': {
                'left_bound': datetime(2015, 12, 3, 12, 8, 0),
                'right_bound': datetime(2015, 12, 3, 12, 8, 11)
            }
        }  # yapf: disable

        super_parser_groups = [('date', datetime(2015, 12, 3, 12, 8, 9))]
        investigation_step = InvestigationStep(None, search_ranges)
        assert investigation_step.compare_with_bound(
            InvestigationStep.LEFT_BOUND, super_parser_groups
        ) == CompareResult.GT
        assert investigation_step.compare_with_bound(
            InvestigationStep.RIGHT_BOUND, super_parser_groups
        ) == CompareResult.LT

        super_parser_groups = [('date', datetime(2015, 12, 3, 12, 8, 0))]
        assert investigation_step.compare_with_bound(
            InvestigationStep.LEFT_BOUND, super_parser_groups
        ) == CompareResult.EQ

        super_parser_groups = [('int', 1)]
        assert investigation_step.compare_with_bound(
            InvestigationStep.LEFT_BOUND, super_parser_groups
        ) == CompareResult.LT
        assert investigation_step.compare_with_bound(
            InvestigationStep.RIGHT_BOUND, super_parser_groups
        ) == CompareResult.GT

        assert investigation_step.compare_with_bound(
            InvestigationStep.LEFT_BOUND, []
        ) == CompareResult.LT
        assert investigation_step.compare_with_bound(
            InvestigationStep.RIGHT_BOUND, []
        ) == CompareResult.GT
