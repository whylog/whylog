from datetime import datetime
from unittest import TestCase

from whylog.constraints import (
    DifferentConstraint, IdenticalConstraint, TimeConstraint, ValueDeltaConstraint
)
from whylog.constraints.exceptions import ConstructorGroupsCountError, ConstructorParamsError


class TestValueDeltaConstraint(TestCase):
    def setUp(self):
        self.constraint_class = ValueDeltaConstraint

    def test_constructor_insufficient_groups(self):
        insufficient_groups = [(0, 1)]
        insufficient_groups_2 = [(0, 1), (1, 2), (2, 3)]
        params = {self.constraint_class.MIN_DELTA: 1}
        self.assertRaises(
            ConstructorGroupsCountError, self.constraint_class, insufficient_groups, params
        )
        self.assertRaises(
            ConstructorGroupsCountError, self.constraint_class, insufficient_groups_2, params
        )

    def test_constructor_wrong_params_names(self):
        groups = [(0, 1), (2, 1)]

        wrong_params = {"sth": 1}
        self.assertRaises(ConstructorParamsError, self.constraint_class, groups, wrong_params)

        mixed_params = {self.constraint_class.MIN_DELTA: 33, "sth": 1}
        self.assertRaises(ConstructorParamsError, self.constraint_class, groups, mixed_params)

    def test_get_group_count(self):
        assert self.constraint_class.get_groups_count() == (2, 2)

    def test_get_param_names(self):
        assert set(self.constraint_class.get_param_names()) == set(
            [self.constraint_class.MIN_DELTA, ValueDeltaConstraint.MAX_DELTA]
        )

    def test_verify_method(self):
        param_dict = {
            self.constraint_class.MIN_DELTA: 1,
            self.constraint_class.MAX_DELTA: 10,
        }
        constraint = self.constraint_class(param_dict=param_dict, params_checking=False)
        assert constraint.verify([100, 110])
        # TODO Add special test for ordered version
        # assert constraint.verify([110, 100])
        assert constraint.verify([100, 101])
        assert constraint.verify([100, 100]) is False
        assert constraint.verify([100, 111]) is False


class TestTimeConstraint(TestValueDeltaConstraint):
    def setUp(self):
        self.constraint_class = TimeConstraint

    def _simple_date(self, seconds):
        # seconds should be between 0 and 60
        return datetime(2016, 5, 19, 8, 35, seconds)

    def test_verify_method(self):
        param_dict = {
            self.constraint_class.MIN_DELTA: 1,
            self.constraint_class.MAX_DELTA: 10,
        }
        constraint = self.constraint_class(param_dict=param_dict, params_checking=False)
        assert constraint.verify([self._simple_date(30), self._simple_date(40)])
        assert constraint.verify([self._simple_date(40), self._simple_date(41)])
        assert constraint.verify([self._simple_date(40), self._simple_date(40)]) is False
        assert constraint.verify([self._simple_date(40), self._simple_date(51)]) is False


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
        assert not IdenticalConstraint.get_param_names()

    def test_get_group_count(self):
        assert IdenticalConstraint.get_groups_count() == (2, None)

    def test_verify_success(self):
        ic = IdenticalConstraint(params_checking=False)
        assert ic.verify(['comp1', 'comp1', 'comp1'])

    def test_verify_fail(self):
        ic = IdenticalConstraint(params_checking=False)
        assert not ic.verify(['comp1', 'hello', 'comp1'])


class TestDifferentConstraint(TestCase):
    def test_get_param_names(self):
        assert set(DifferentConstraint.get_param_names()) == set([DifferentConstraint.PARAM_VALUE])

    def test_verify_success(self):
        ic = DifferentConstraint(params_checking=False)
        assert ic.verify(['foo', 'bar', 'juj'])

    def test_verify_fail(self):
        ic = DifferentConstraint(params_checking=False)
        assert not ic.verify(['comp1', 'comp1', 'foo'])
