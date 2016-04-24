from whylog.constraints import *
from whylog.exceptions import WhylogError


class ConstraintManager(object):
    @classmethod
    def get_constraint_by_type(cls, constraint_data):
        constraints = {
            'identical':    IdenticalIntervals({}),
            'time':         TimeConstraint(constraint_data)
            # register your constraint here
        }
        if constraint_data['name'] in constraints:
            return constraints[constraint_data['name']]
        raise WhylogError("No such constraint (%s) registered" % constraint_data['name'])


class Verifier(object):
    def verify_rule(self, rule, clues):
        pass

    @classmethod
    def _clues_combinations(cls, clues_lists, collected_subset=[]):
        """
        recursive generator that returns all combinations
        of elements from lists contained in clues_lists
        example:
        >>> xs = [[1, 2, 3], [4, 5], [6]]
        >>> for l in Verifier._clues_combinations(xs):
        >>>     print l
        [1, 4, 6]
        [1, 5, 6]
        [2, 4, 6]
        [2, 5, 6]
        [3, 4, 6]
        [3, 5, 6]
        it always should be called with empty accumulator,
        that is collected_subset=[]
        """
        if len(clues_lists) != 0:
            for clue in clues_lists[0]:
                for subset in cls._clues_combinations(clues_lists[1:], collected_subset + [clue]):
                    yield subset
        else:
            yield collected_subset

    @classmethod
    def constraints_and(cls, clues_lists, constraints):
        clues_lists = filter(lambda x: x, clues_lists)
        causes = []
        for combination in cls._clues_combinations(clues_lists):
            if all(ConstraintManager.get_constraint_by_type(constraint).verify(constraint['params'], combination)
                   for constraint in constraints):
                # FIXME verify has not established signature yet
                causes.append(combination)
        return causes

    @classmethod
    def constraints_or(cls, clues_lists, constraints):
        clues_lists = filter(lambda x: x, clues_lists)
        causes = []
        for combination in cls._clues_combinations(clues_lists):
            if any(ConstraintManager.get_constraint_by_type(constraint).verify(constraint['params'], combination)
                   for constraint in constraints):
                # FIXME verify has not established signature yet
                causes.append(combination)
        return causes
