import datetime
import itertools
from abc import ABCMeta, abstractmethod, abstractproperty

import six

from whylog.constraints.const import ConstraintType
from whylog.converters import ConverterType, get_converter
from whylog.converters.exceptions import ConverterError
from whylog.teacher.user_intent import UserConstraintIntent

from whylog.constraints.exceptions import (  # isort:skip
    ConstructorGroupsCountError, ConstructorParamsError
)
from whylog.constraints.validation_problems import (  # isort:skip
    MinGreaterThatMaxProblem, NoTimeDeltasProblem, ParamConversionProblem
)


@six.add_metaclass(ABCMeta)
class AbstractConstraint(object):
    """
    :param MIN_GROUPS_COUNT: minimal groups count needed to create constraint
    :param MAX_GROUPS_COUNT: maximal groups count needed to create constraint
    """

    @abstractproperty
    def TYPE(self):
        """
        Constraint type name. Must be unique for each constraint.
        """
        pass

    MIN_GROUPS_COUNT = 2

    MAX_GROUPS_COUNT = None

    @abstractproperty
    def PARAMS(self):
        """
        Params names and converters.
        Constraint construction requires a dict[param name, param value].
        Some of then can be optional.
        """
        pass

    def __init__(self, groups=None, param_dict=None, params_checking=True):
        """
        For Teacher and Front use while creating user rule.
        :param param_dict: dict of additional params of constraint
        :param groups: all groups that are linked by constraint,
                       represented by list of tuples (line_id, group_no),
                       where line_id and group_no is inner numeration between Front and Teacher
        """
        self.groups = groups or []
        self.params = param_dict or {}
        if params_checking:
            self._check_constructor_groups()
            self._check_constructor_params_occurrence()

    def _check_constructor_groups(self):
        groups_count = len(self.groups)
        if (self.MIN_GROUPS_COUNT is not None and groups_count < self.MIN_GROUPS_COUNT) \
                or (self.MAX_GROUPS_COUNT is not None and groups_count > self.MAX_GROUPS_COUNT):
            raise ConstructorGroupsCountError(
                self.TYPE, len(self.groups), self.MIN_GROUPS_COUNT, self.MAX_GROUPS_COUNT
            )

    def _check_constructor_params_occurrence(self):
        correct_param_names = set(self.get_param_names())
        actual_param_names = set(self.params.keys())
        self._check_useless_params(correct_param_names, actual_param_names)
        self._check_mandatory_params(correct_param_names, actual_param_names)

    def _check_useless_params(self, correct_param_names, actual_param_names):
        if actual_param_names - correct_param_names:
            raise ConstructorParamsError(self.TYPE, correct_param_names, actual_param_names)

    def _check_mandatory_params(self, correct_param_names, actual_param_names):
        """
        Verifies mandatory params used to construct Constraint
        Throws exception if params don't meet requirements
        """
        pass

    def convert_to_user_constraint_intent(self, constraint_id=None):
        """
        Converts constraint to UserConstraintIntent object.

        For Teacher and Config use while saving constraint into Whylog knowledge base.
        """
        return UserConstraintIntent(self.TYPE, self.groups, self.params, constraint_id)

    @classmethod
    def get_param_names(cls):
        """
        Returns names of constraint additional params.
        For Front to display param names to user and then ask user for param contents.
        """
        return cls.PARAMS.keys()

    @classmethod
    def get_groups_count(cls):
        """
        Returns minimal and maximal count of groups needed to create constraint.
        For Front to ask user for proper count of groups.
        2, None - at least 2 groups
        2, 2 - exactly 2 groups
        """
        return cls.MIN_GROUPS_COUNT, cls.MAX_GROUPS_COUNT

    @abstractmethod
    def verify(self, group_contents):
        """
        Verifies constraint for given params in param_dict and groups contents.

        :param groups: list of groups contents,

        For LogReader and Teacher verification.
        It must be optimized as well as possible (for LogReader).
        """

        pass

    def _convert_params_values(self):
        problems = []
        for param_name, converter_type in six.iteritems(self.PARAMS):
            param_val = self.params.get(param_name)
            if param_val is not None:
                converter = get_converter(converter_type)
                try:
                    converted_val = converter.safe_convert(param_val)
                except ConverterError:
                    problems.append(ParamConversionProblem(param_name, param_val, converter_type))
                else:
                    self.params[param_name] = converted_val
        return problems

    def _validate_params(self):
        return self._convert_params_values()

    def _validate_groups(self):
        # TODO: implement
        return []

    def validate(self):
        """
        Validates constraint: verifies if it is ready to save
        """
        return self._validate_params() + self._validate_groups()


class ValueDeltaConstraint(AbstractConstraint):
    """
    Value delta between values must be greater than 'min_delta' and lower than 'max_delta'
    """

    TYPE = ConstraintType.VALUE_DELTA

    MAX_GROUPS_COUNT = 2

    MIN_DELTA = 'min_delta'
    MAX_DELTA = 'max_delta'

    PARAMS = {MIN_DELTA: ConverterType.TO_FLOAT, MAX_DELTA: ConverterType.TO_FLOAT}

    @classmethod
    def convert(cls, value):
        return float(value)

    def __init__(self, groups=None, param_dict=None, params_checking=True):
        super(ValueDeltaConstraint, self).__init__(groups, param_dict, params_checking)
        if not params_checking:
            param_min_delta = self.params.get(self.MIN_DELTA)
            param_max_delta = self.params.get(self.MAX_DELTA)
            assert param_min_delta is not None or param_max_delta is not None
            if param_min_delta is not None and param_max_delta is not None:
                self.verify = self._verify_both
                self._min_delta = self.convert(param_min_delta)
                self._max_delta = self.convert(param_max_delta)
            elif param_max_delta is not None:
                self.verify = self._verify_max
                self._max_delta = self.convert(param_max_delta)
            elif param_min_delta is not None:
                self.verify = self._verify_min
                self._min_delta = self.convert(param_min_delta)

    def _verify_min(self, group_contents):
        first_value, second_value = group_contents
        return second_value - first_value >= self._min_delta

    def _verify_max(self, group_contents):
        first_value, second_value = group_contents
        return second_value - first_value <= self._max_delta

    def _verify_both(self, group_contents):
        first_value, second_value = group_contents
        return self._max_delta >= second_value - first_value >= self._min_delta

    # TODO add parametr ordered
    def _verify_ordered_min(self, group_contents):
        first_value, second_value = group_contents
        return abs(second_value - first_value) >= self._min_delta

    def _verify_ordered_max(self, group_contents):
        first_value, second_value = group_contents
        return abs(second_value - first_value) <= self._max_delta

    def _verify_ordered_both(self, group_contents):
        first_value, second_value = group_contents
        return self._max_delta >= abs(second_value - first_value) >= self._min_delta

    def verify(self, group_contents):
        pass

    def _validate_params(self):
        problems = super(ValueDeltaConstraint, self)._validate_params()
        param_min_delta = self.params.get(self.MIN_DELTA)
        param_max_delta = self.params.get(self.MAX_DELTA)
        if param_min_delta is None and param_max_delta is None:
            problems.append(NoTimeDeltasProblem(self.MIN_DELTA, self.MAX_DELTA))
        if param_min_delta is not None and param_max_delta is not None:
            if param_min_delta > param_max_delta:
                problems.append(MinGreaterThatMaxProblem())
        return problems


class TimeConstraint(ValueDeltaConstraint):
    """
    Time delta between two dates must be greater or equal to 'min_delta'
    and lower or equal to 'max_delta'
    I.e:
    TimeConstraint(
        [(0, 1), (2, 1)]
        {'min_delta': datetime.timedelta(seconds=1), 'max_delta': datetime.timedelta(seconds=10)},
    )
    :param groups: First element of groups is a group with earlier date.
    """

    TYPE = ConstraintType.TIME_DELTA

    @classmethod
    def convert(cls, value):
        return datetime.timedelta(seconds=value)


class IdenticalConstraint(AbstractConstraint):
    """
    Contents of groups must be identical.
    I.e:
    IdenticalConstraint([(1, 2), (2, 4)])
    """

    TYPE = ConstraintType.IDENTICAL

    PARAMS = {}

    def verify(self, group_contents):
        """
        I.e:
        - verify(['comp1', 'comp1', 'comp1'], {}) returns True
        - verify(['comp1', 'hello', 'comp1'], {}) returns False
        """
        return all(group_contents[0] == group for group in group_contents)


class DifferentConstraint(AbstractConstraint):
    """
    Contents of groups must be different.
    """

    TYPE = ConstraintType.DIFFERENT

    PARAM_VALUE = "value"
    PARAMS = {PARAM_VALUE: ConverterType.TO_STRING}

    def __init__(self, groups=None, param_dict=None, params_checking=True):
        super(DifferentConstraint, self).__init__(groups, param_dict, params_checking)
        param_dict = param_dict or {}
        self.diff_value = param_dict.get(self.PARAM_VALUE)

    def verify(self, group_contents):
        if self.diff_value:
            # I'm not sure if it is correct implementation.
            return len(set(itertools.chain(group_contents, [self.diff_value]))
                      ) == len(group_contents) + 1
        else:
            return len(set(group_contents)) == len(group_contents)


class HeteroConstraint(AbstractConstraint):
    """
    A number of groups must be identical, the rest must be different.
    """

    TYPE = ConstraintType.HETERO
