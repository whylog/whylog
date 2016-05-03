from datetime import datetime, timedelta
from unittest import TestCase

from whylog.user_constraints.exceptions import ConstructorGroupsCountError, ConstructorParamsError
from whylog.user_constraints import IdenticalConstraint, TimeConstraint


class TestIdenticalConstraint(TestCase):
    def test_constructor_insufficient_groups(self):
        insufficient_groups = [(0, 1)]
        self.assertRaises(ConstructorGroupsCountError, IdenticalConstraint, insufficient_groups)

    def test_constructor_not_empty_params(self):
        self.assertRaises(
            ConstructorParamsError, IdenticalConstraint, [
                (0, 1), (2, 1)
            ], {'sth': 12}
        )

    def test_get_param_names(self):
        assert IdenticalConstraint.get_param_names() == []

    def test_get_group_count(self):
        assert IdenticalConstraint.get_groups_count() == (2, None)

    def test_verify_success(self):
        ic = IdenticalConstraint(params_checking=False)
        assert ic.verify(['comp1', 'comp1', 'comp1'])

    def test_verify_fail(self):
        ic = IdenticalConstraint(params_checking=False)
        assert not ic.verify(['comp1', 'hello', 'comp1'])


class TestTimeConstraint(TestCase):
    def setUp(self):
        self.min_delta = timedelta(seconds=1)
        self.max_delta = timedelta(seconds=10)
        self.lower_date = datetime(2016, 5, 19, 8, 35, 1)
        self.greater_date = datetime(2016, 5, 19, 8, 35, 5)

    def test_constructor_insufficient_groups(self):
        insufficient_groups = [(0, 1)]
        params = {TimeConstraint.MIN_DELTA: self.min_delta}
        self.assertRaises(ConstructorGroupsCountError, TimeConstraint, insufficient_groups, params)

    def test_constructor_wrong_params(self):
        groups = [(0, 1), (2, 1)]
        no_params = {}
        self.assertRaises(ConstructorParamsError, TimeConstraint, groups, no_params)

        wrong_params = {"sth": 1}
        self.assertRaises(ConstructorParamsError, TimeConstraint, groups, wrong_params)

        mixed_params = {TimeConstraint.MIN_DELTA: 33, "sth": 1}
        self.assertRaises(ConstructorParamsError, TimeConstraint, groups, mixed_params)

    def test_get_group_count(self):
        assert TimeConstraint.get_groups_count() == (2, 2)

    def test_verify_success(self):
        tc = TimeConstraint(params_checking=False)
        assert tc.verify(
            [self.lower_date, self.greater_date], {
                TimeConstraint.MIN_DELTA: self.min_delta,
                TimeConstraint.MAX_DELTA: self.max_delta
            }
        )

    def test_verify_fail(self):
        tc = TimeConstraint(params_checking=False)
        assert not tc.verify(
            [self.greater_date, self.lower_date], {
                TimeConstraint.MIN_DELTA: self.min_delta,
                TimeConstraint.MAX_DELTA: self.max_delta
            }
        )
