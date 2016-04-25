from whylog.constraints import IdenticalIntervals, TimeConstraint
from whylog.exceptions import WhylogError
from whylog.front import FrontInput


class ConstraintManager(object):
    @classmethod
    def get_constraint_by_type(cls, constraint_data):
        constraints = {
            'identical': IdenticalIntervals({}),
            'time': TimeConstraint({})
            # register your constraint here
        }
        if constraint_data['name'] in constraints:
            return constraints[constraint_data['name']]
        raise WhylogError("No such constraint (%s) registered" % constraint_data['name'])


class Verifier(object):
    @classmethod
    def _front_input_from_clue(cls, clue):
        return FrontInput(clue.line_offset, clue.line_prefix_content, clue.line_source)

    @classmethod
    def _verify_constraint(cls, combination, effect, constraint):
        constraint_verifier = ConstraintManager.get_constraint_by_type(constraint)
        groups = []
        for group_info in constraint['clues_groups']:
            parser_num, group_num = group_info[0], group_info[1]
            if parser_num == 0:
                groups.append(effect.regex_parameters[group_num - 1])
            else:
                groups.append(combination[parser_num - 1].regex_parameters[group_num - 1])
        return constraint_verifier.verify(constraint['params'], groups)

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
    def constraints_and(cls, clues_lists, effect, constraints):
        clues_lists = list(filter(lambda x: x, clues_lists))
        causes = []
        for combination in cls._clues_combinations(clues_lists):
            if all(
                cls._verify_constraint(combination, effect, constraint)
                for constraint in constraints
            ):
                causes.append(
                    InvestigationResult(
                        [cls._front_input_from_clue(clue) for clue in combination], constraints
                    )
                )
        return causes

    @classmethod
    def constraints_or(cls, clues_lists, effect, constraints):
        clues_lists = list(filter(lambda x: x, clues_lists))
        causes = []
        for combination in cls._clues_combinations(clues_lists):
            verified_constraints = list(
                filter(
                    lambda constraint: cls._verify_constraint(combination, effect, constraint),
                    constraints
                )
            )
            if len(verified_constraints) > 0:
                causes.append(
                    InvestigationResult(
                        [
                            cls._front_input_from_clue(clue) for clue in combination
                        ], verified_constraints
                    )
                )
        return causes


class InvestigationResult(object):
    def __init__(self, lines, constraints):
        self.lines = lines
        self.constraints = constraints

    def __repr__(self):
        return "\n(\n    result lines: %s;\n    due to constraints: %s\n)" % (
            self.lines, self.constraints
        )

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
