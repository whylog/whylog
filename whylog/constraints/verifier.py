from whylog.config import Clue
from whylog.constraints import IdenticalIntervals, TimeConstraint
from whylog.constraints.exceptions import UnsupportedConstraintTypeError
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
        raise UnsupportedConstraintTypeError(constraint_data)


class Verifier(object):
    UNMATCHED = Clue(None, None, None, None)

    @classmethod
    def _front_input_from_clue(cls, clue):
        return FrontInput(clue.line_offset, clue.line_prefix_content, clue.line_source)

    @classmethod
    def _create_investigation_result(cls, clues_combination, constraints):
        return InvestigationResult(
            [cls._front_input_from_clue(clue) for clue in clues_combination], constraints
        )

    @classmethod
    def _verify_constraint(cls, combination, effect, constraint):
        """
        checks if specified clues (which represents parsers: 1,2,.. for some rule) and
        effect (which represents parser 0 from this rule) satisfy one given constraint.
        returns True if so, or False otherwise
        """
        constraint_verifier = ConstraintManager.get_constraint_by_type(constraint)
        groups = []
        for group_info in constraint['clues_groups']:
            parser_num, group_num = group_info
            if parser_num == 0:
                groups.append(effect.regex_parameters[group_num - 1])
            else:
                if combination[parser_num - 1] == Verifier.UNMATCHED:
                    return False
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
        clues_lists = [clues if clues else [Verifier.UNMATCHED] for clues in clues_lists]
        causes = []
        for combination in cls._clues_combinations(clues_lists):
            if all(
                cls._verify_constraint(combination, effect, constraint)
                for constraint in constraints
            ):
                causes.append(cls._create_investigation_result(combination, constraints))
        return causes

    @classmethod
    def constraints_or(cls, clues_lists, effect, constraints):
        clues_lists = [clues if clues else [Verifier.UNMATCHED] for clues in clues_lists]
        causes = []
        for combination in cls._clues_combinations(clues_lists):
            verified_constraints = [
                constraint
                for constraint in constraints
                if cls._verify_constraint(combination, effect, constraint)
            ]
            if len(verified_constraints) > 0:
                causes.append(
                    cls._create_investigation_result(
                        [
                            clue for clue in combination if not clue == Verifier.UNMATCHED
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
