import six

from whylog.constraints import (DifferentConstraint, HeteroConstraint, IdenticalConstraint,
                                TimeConstraint, ValueDeltaConstraint) # yapf: disable
from whylog.constraints.const import ConstraintType
from whylog.constraints.exceptions import UnsupportedConstraintTypeError


class ConstraintRegistry(object):
    CONSTRAINTS = {
        ConstraintType.DIFFERENT: DifferentConstraint,
        ConstraintType.IDENTICAL: IdenticalConstraint,
        ConstraintType.TIME_DELTA: TimeConstraint,
        ConstraintType.VALUE_DELTA: ValueDeltaConstraint,
        ConstraintType.HETERO: HeteroConstraint,
        # register your constraint here
    }  # yapf: disable

    @classmethod
    def get_constraint(cls, constraint_data):
        if constraint_data['name'] in cls.CONSTRAINTS:
            return cls.CONSTRAINTS[constraint_data['name']](
                param_dict=constraint_data['params'],
                params_checking=False
            )
        raise UnsupportedConstraintTypeError(constraint_data)

    @classmethod
    def constraint_from_name(cls, constraint_name):
        return cls.CONSTRAINTS.get(constraint_name)

    @classmethod
    def get_types(cls):
        return six.iterkeys(cls.CONSTRAINTS)


class ConstraintManager(object):
    """
    there should be one such object per rule being verified
    """

    def __init__(self):
        self._actual_constraints = {}

    def __getitem__(self, constraint_data):
        constraint = self._actual_constraints.get(constraint_data['name'])
        if constraint is None:
            constraint_verifier = ConstraintRegistry.get_constraint(constraint_data)
            self._actual_constraints[constraint_data['name']] = constraint_verifier
        return self._actual_constraints[constraint_data['name']]
