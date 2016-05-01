from unittest import TestCase

from whylog.config.investigation_plan import Clue, LineSource
from whylog.constraints.verifier import ConstraintManager, InvestigationResult, Verifier
from whylog.front import FrontInput


class TestBasic(TestCase):
    def test_clues_combinations_basic(self):
        xs = [([1, 2, 3], 2), ([4, 5], 1)]
        combinations = list(Verifier._clues_combinations(xs))
        assert combinations == [
            [1, 2, 4],
            [1, 2, 5],
            [1, 3, 4],
            [1, 3, 5],
            [2, 1, 4],
            [2, 1, 5],
            [2, 3, 4],
            [2, 3, 5],
            [3, 1, 4],
            [3, 1, 5],
            [3, 2, 4],
            [3, 2, 5]
        ]  # yapf: disable

    def test_constraints_or_basic(self):
        line_source = LineSource('localhost', 'node_0.log')
        effect = Clue(('Banana', 2), 'Banana, 2 times', 3000, line_source)
        clues_lists = [
            ([
                Clue(('Milk', 3), 'Milk, 3 times', 50, line_source),
                Clue(('Chocolate', 2), 'Chocolate, 2 times', 100, line_source),
                Clue(('Banana', 1), 'Banana, 1 times', 150, line_source)
            ], 1), ([
                Clue(('Banana', 2), 'Banana, 2 times', 1050, line_source),
                Clue(('Milk', 1), 'Milk, 1 times', 1100, line_source)
            ], 1)
        ]  # yapf: disable
        constraints = [
            {
                'clues_groups': [[0, 1], [1, 1], [2, 1]],
                'name': 'identical',
                'params': {}
            }, {
                'clues_groups': [[0, 2], [1, 2], [2, 2]],
                'name': 'identical',
                'params': {}
            }
        ]
        causes = Verifier.constraints_or(clues_lists, effect, constraints, ConstraintManager())
        assert len(causes) == 2
        assert all(isinstance(cause, InvestigationResult) for cause in causes)

        assert all(cause.constraints_linkage == InvestigationResult.OR for cause in causes)
        assert causes[0].lines == [
            FrontInput.from_clue(Clue(
                ('Chocolate', 2), 'Chocolate, 2 times', 100, line_source)),
            FrontInput.from_clue(Clue(
                ('Banana', 2), 'Banana, 2 times', 1050, line_source))
        ]  # yapf: disable
        assert causes[1].lines == [
            FrontInput.from_clue(Clue(
                ('Banana', 1), 'Banana, 1 times', 150, line_source)),
            FrontInput.from_clue(Clue(
                ('Banana', 2), 'Banana, 2 times', 1050, line_source))
        ]  # yapf: disable

    def test_constraints_and_basic(self):
        line_source = LineSource('localhost', 'node_0.log')
        effect = Clue(('Pear', 2), 'Pear, 2 times', 3000, line_source)
        clues_lists = [
            ([
                Clue(('Milk', 3), 'Milk, 3 times', 50, line_source),
                Clue(('Chocolate', 2), 'Chocolate, 2 times', 100, line_source),
                Clue(('Pear', 2), 'Pear, 2 times', 150, line_source)
            ], 1), ([
                Clue(('Pear', 2), 'Pear, 2 times', 1050, line_source),
                Clue(('Milk', 1), 'Milk, 1 times', 1100, line_source)
            ], 1)
        ]  # yapf: disable
        constraints = [
            {
                'clues_groups': [[0, 1], [1, 1], [2, 1]],
                'name': 'identical',
                'params': {}
            }, {
                'clues_groups': [[0, 2], [1, 2], [2, 2]],
                'name': 'identical',
                'params': {}
            }
        ]
        causes = Verifier.constraints_and(clues_lists, effect, constraints, ConstraintManager())
        assert len(causes) == 1
        assert all(isinstance(cause, InvestigationResult) for cause in causes)

        assert all(cause.constraints_linkage == InvestigationResult.AND for cause in causes)
        assert causes[0].lines == [
            FrontInput.from_clue(Clue(
                ('Pear', 2), 'Pear, 2 times', 150, line_source)),
            FrontInput.from_clue(Clue(
                ('Pear', 2), 'Pear, 2 times', 1050, line_source))
        ]  # yapf: disable

    def test_unmatched_clues_comparison(self):
        unmatched_clue = Clue(None, None, None, None)
        assert unmatched_clue == Verifier.UNMATCHED

    def test_constraints_when_one_unmatched(self):
        line_source = LineSource('localhost', 'node_0.log')
        effect = Clue(('Banana', 2), 'Banana, 2 times', 3000, line_source)
        clues_lists = [
            ([
            ], 1), ([
                Clue(('Banana', 2), 'Banana, 2 times', 1050, line_source),
                Clue(('Milk', 1), 'Milk, 1 times', 1100, line_source)
            ], 1)
        ]  # yapf: disable
        constraints = [
            {
                'clues_groups': [[0, 1], [1, 1], [2, 1]],
                'name': 'identical',
                'params': {}
            }, {
                'clues_groups': [[0, 2], [2, 2]],
                'name': 'identical',
                'params': {}
            }
        ]

        # testing 'or'
        causes = Verifier.constraints_or(clues_lists, effect, constraints, ConstraintManager())
        assert len(causes) == 1
        assert all(isinstance(cause, InvestigationResult) for cause in causes)

        assert all(cause.constraints_linkage == InvestigationResult.OR for cause in causes)
        assert causes[0].lines == [
            FrontInput.from_clue(Clue(
                ('Banana', 2), 'Banana, 2 times', 1050, line_source))
        ]  # yapf: disable
        assert causes[0].constraints == [
            {
                'clues_groups': [[0, 2], [2, 2]],
                'name': 'identical',
                'params': {}
            }
        ]

        # testing 'and'
        causes = Verifier.constraints_and(clues_lists, effect, constraints, ConstraintManager())
        assert not causes

    def test_constraints_and_verification_failed_when_or_succeeded(self):
        line_source = LineSource('localhost', 'node_0.log')
        effect = Clue(('Banana', 44), 'Banana, 44 times', 3000, line_source)
        clues_lists = [
            ([
                Clue(('Milk', 3), 'Milk, 3 times', 50, line_source),
                Clue(('Chocolate', 4), 'Chocolate, 4 times', 100, line_source),
                Clue(('Pear', 2), 'Pear, 2 times', 150, line_source)                # <- should be found (parser 1)
            ], 1), ([
                Clue(('Pineapple', 2), 'Pineapple, 2 times', 1050, line_source),    # <- should be found (parser 2)
                Clue(('Milk', 1), 'Milk, 1 times', 1100, line_source)
            ], 1)
        ]  # yapf: disable
        constraints = [
            {
                'clues_groups': [[0, 1], [1, 1], [2, 1]],
                'name': 'identical',
                'params': {}
            }, {
                'clues_groups': [[1, 2], [2, 2]],
                'name': 'identical',
                'params': {}
            }
        ]

        # testing 'and'
        causes = Verifier.constraints_and(clues_lists, effect, constraints, ConstraintManager())
        assert not causes

        # testing 'or'
        causes = Verifier.constraints_or(clues_lists, effect, constraints, ConstraintManager())
        assert len(causes) == 1
        assert all(isinstance(cause, InvestigationResult) for cause in causes)

        assert all(cause.constraints_linkage == InvestigationResult.OR for cause in causes)
        assert causes[0].lines == [
            FrontInput.from_clue(Clue(
                ('Pear', 2), 'Pear, 2 times', 150, line_source)),
            FrontInput.from_clue(Clue(
                ('Pineapple', 2), 'Pineapple, 2 times', 1050, line_source))
        ]  # yapf: disable
        assert causes[0].constraints == [
            {
                'clues_groups': [[1, 2], [2, 2]],
                'name': 'identical',
                'params': {}
            }
        ]

    def test_constraints_or_verification_failed(self):
        line_source = LineSource('localhost', 'node_0.log')
        effect = Clue(('Pineapple', 44), 'Pineapple, 44 times', 3000, line_source)
        clues_lists = [
            ([
                Clue(('Milk', 3), 'Milk, 3 times', 50, line_source),
                Clue(('Chocolate', 2), 'Chocolate, 2 times', 100, line_source),
                Clue(('Banana', 1), 'Banana, 1 times', 150, line_source)
            ], 1), ([
                Clue(('Banana', 2), 'Banana, 2 times', 1050, line_source),
                Clue(('Milk', 1), 'Milk, 2 times', 1100, line_source)
            ], 1)
        ]  # yapf: disable
        constraints = [
            {
                'clues_groups': [[0, 1], [1, 1], [2, 1]],
                'name': 'identical',
                'params': {}
            }, {
                'clues_groups': [[0, 2], [1, 2], [2, 2]],
                'name': 'identical',
                'params': {}
            }
        ]
        causes = Verifier.constraints_or(clues_lists, effect, constraints, ConstraintManager())
        assert not causes

    def test_constraints_or_without_constraints(self):
        line_source = LineSource('localhost', 'node_0.log')
        effect = Clue(('Pineapple', 44), 'Pineapple, 44 times', 3000, line_source)
        clues_lists = [
            ([
                Clue(('Banana', 2), 'Banana, 2 times', 1050, line_source),
                Clue(('Milk', 1), 'Milk, 2 times', 1100, line_source)
            ], 1),
            ([
                Clue(('Chocolate', 2), 'Chocolate, 2 times', 100, line_source)
            ], 1)
        ]  # yapf: disable
        constraints = []

        causes = Verifier.constraints_or(clues_lists, effect, constraints, ConstraintManager())
        assert len(causes) == 2
        assert all(isinstance(cause, InvestigationResult) for cause in causes)

        assert all(cause.constraints_linkage == InvestigationResult.OR for cause in causes)
        assert causes[0].lines == [
            FrontInput.from_clue(Clue(
                ('Banana', 2), 'Banana, 2 times', 1050, line_source)),
            FrontInput.from_clue(Clue(
                ('Chocolate', 2), 'Chocolate, 2 times', 100, line_source))
        ]  # yapf: disable
        assert causes[1].lines == [
            FrontInput.from_clue(Clue(
                ('Milk', 1), 'Milk, 2 times', 1100, line_source)),
            FrontInput.from_clue(Clue(
                ('Chocolate', 2), 'Chocolate, 2 times', 100, line_source))
        ]  # yapf: disable
        assert all(not cause.constraints for cause in causes)

    def test_single_constraint_not_basic(self):
        line_source = LineSource('localhost', 'node_0.log')
        effect = Clue(('Dinner', 44), 'Dinner, 44 times', 440, line_source)
        clues_lists = [
            ([
                Clue(('Car', 40), 'Car, 40 times', 400, line_source),
                Clue(('Car', 1), 'Car, 1 times', 100, line_source),
                Clue(('Car', 15), 'Car, 15 times', 150, line_source)
            ], 1),
            ([
                Clue(('Forest', 0), 'Forest, 0 times', 0, line_source),
                Clue(('Forest', 3), 'Forest, 3 times', 30, line_source),
                Clue(('Forest', 42), 'Forest, 42 times', 420, line_source)
            ], 1)
        ]  # yapf: disable
        constraint = {
            'clues_groups': [[0, 1], [1, 1], [2, 1]],
            'name': 'identical',
            'params': {}
        }
        causes = Verifier.single_constraint_not(clues_lists, effect, constraint, ConstraintManager())

        assert len(causes) == 1
        assert all(isinstance(cause, InvestigationResult) for cause in causes)
        assert causes[0].constraints_linkage == InvestigationResult.NOT
        assert causes[0].constraints[0] == constraint
