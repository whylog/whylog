from unittest import TestCase

from whylog.config.investigation_plan import Clue, LineSource
from whylog.constraints.verifier import InvestigationResult, Verifier
from whylog.front import FrontInput


class TestBasic(TestCase):
    def test_clues_combinations_basic(self):
        xs = [[1, 2, 3], [4, 5], [6]]
        combinations = list(Verifier._clues_combinations(xs))
        assert combinations == [
            [1, 4, 6],
            [1, 5, 6],
            [2, 4, 6],
            [2, 5, 6],
            [3, 4, 6],
            [3, 5, 6]
        ]  # yapf: disable

    def test_constraints_or_basic(self):
        line_source = LineSource('localhost', 'node_0.log')
        effect = Clue(('Banana', 2), 'Banana, 2 times', 3000, line_source)
        clues_lists = [
            [
                Clue(('Milk', 3), 'Milk, 3 times', 50, line_source),
                Clue(('Chocolate', 2), 'Chocolate, 2 times', 100, line_source),
                Clue(('Banana', 1), 'Banana, 1 times', 150, line_source)
            ], [
                Clue(('Banana', 2), 'Banana, 2 times', 1050, line_source),
                Clue(('Milk', 1), 'Milk, 2 times', 1100, line_source)
            ]
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
        causes = Verifier.constraints_or(clues_lists, effect, constraints)
        assert len(causes) == 2
        assert all(isinstance(cause, InvestigationResult) for cause in causes)
        assert all(isinstance(line, FrontInput) for line in causes[0].lines + causes[1].lines)

        assert causes[0].lines == [
            Verifier._front_input_from_clue(Clue(
                ('Chocolate', 2), 'Chocolate, 2 times', 100, line_source)),
            Verifier._front_input_from_clue(Clue(
                ('Banana', 2), 'Banana, 2 times', 1050, line_source))
        ]  # yapf: disable
        assert causes[1].lines == [
            Verifier._front_input_from_clue(Clue(
                ('Banana', 1), 'Banana, 1 times', 150, line_source)),
            Verifier._front_input_from_clue(Clue(
                ('Banana', 2), 'Banana, 2 times', 1050, line_source))
        ]  # yapf: disable

    def test_constraints_and_basic(self):
        line_source = LineSource('localhost', 'node_0.log')
        effect = Clue(('Pear', 2), 'Pear, 2 times', 3000, line_source)
        clues_lists = [
            [
                Clue(('Milk', 3), 'Milk, 3 times', 50, line_source),
                Clue(('Chocolate', 2), 'Chocolate, 2 times', 100, line_source),
                Clue(('Pear', 2), 'Pear, 2 times', 150, line_source)
            ], [
                Clue(('Pear', 2), 'Pear, 2 times', 1050, line_source),
                Clue(('Milk', 1), 'Milk, 2 times', 1100, line_source)
            ]
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
        causes = Verifier.constraints_and(clues_lists, effect, constraints)
        assert len(causes) == 1
        assert all(isinstance(cause, InvestigationResult) for cause in causes)

        assert causes[0].lines == [
            Verifier._front_input_from_clue(Clue(
                ('Pear', 2), 'Pear, 2 times', 150, line_source)),
            Verifier._front_input_from_clue(Clue(
                ('Pear', 2), 'Pear, 2 times', 1050, line_source))
        ]  # yapf: disable

    def test_unmatched_clues_comparison(self):
        unmatched_clue = Clue(None, None, None, None)
        assert unmatched_clue == Verifier.UNMATCHED

    def test_constraints_or_when_one_unmatched(self):
        line_source = LineSource('localhost', 'node_0.log')
        effect = Clue(('Banana', 2), 'Banana, 2 times', 3000, line_source)
        clues_lists = [
            [
            ], [
                Clue(('Banana', 2), 'Banana, 2 times', 1050, line_source),
                Clue(('Milk', 1), 'Milk, 1 times', 1100, line_source)
            ]
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
        causes = Verifier.constraints_or(clues_lists, effect, constraints)
        assert len(causes) == 1
        assert all(isinstance(cause, InvestigationResult) for cause in causes)
        assert all(isinstance(line, FrontInput) for line in causes[0].lines)

        assert causes[0].lines == [
            Verifier._front_input_from_clue(Clue(
                ('Banana', 2), 'Banana, 2 times', 1050, line_source))
        ]  # yapf: disable
        assert causes[0].constraints == [
            {
                'clues_groups': [[0, 2], [2, 2]],
                'name': 'identical',
                'params': {}
            }
        ]
