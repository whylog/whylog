from unittest import TestCase

import six

from whylog.config.investigation_plan import Clue, LineSource
from whylog.config.parsers import RegexParser
from whylog.config.rule import RegexRuleFactory, Rule
from whylog.constraints.verifier import InvestigationResult, Verifier
from whylog.front import FrontInput


class TestBasic(TestCase):
    cause_a = RegexParser('cause_a', '31 carrots', '^(\d\d) carrots$', [1], 'default', {1: 'int'})
    cause_b = RegexParser('cause_b', '79 broccoli', '^(\d\d) broccoli$', [1], 'default', {1: 'int'})
    effect = RegexParser('effect', '53 dinners', '^(\d\d) carrots$', [1], 'default', {1: 'int'})
    line_source = LineSource('localhost', 'node_1.log')

    def test_order_causes_list(self):
        cause_1 = RegexParser('cause_a', None, '', None, None, None)
        cause_2 = RegexParser('cause_b', None, '', None, None, None)
        cause_3 = RegexParser('cause_c', None, '', None, None, None)

        causes = [cause_2, cause_3, cause_2, cause_1]
        constraints = [
            {
                'clues_groups': [[0, 1], [1, 3], [2, 4], [3, 7], [4, 2]],
                'name': 'identical',
                'params': {}
            }, {
                'clues_groups': [[0, 1], [4, 2]],
                'name': 'identical',
                'params': {}
            }
        ]

        sorted_causes, modified_constrains = RegexRuleFactory._order_causes_list(
            causes, constraints
        )

        option_1 = [
            {
                'clues_groups': [[0, 1], [2, 3], [4, 4], [3, 7], [1, 2]],
                'name': 'identical',
                'params': {}
            }, {
                'clues_groups': [[0, 1], [1, 2]],
                'name': 'identical',
                'params': {}
            }
        ]
        option_2 = [
            {
                'clues_groups': [[0, 1], [3, 3], [4, 4], [2, 7], [1, 2]],
                'name': 'identical',
                'params': {}
            }, {
                'clues_groups': [[0, 1], [1, 2]],
                'name': 'identical',
                'params': {}
            }
        ]
        assert all(
            sorted_causes[i].name <= sorted_causes[i + 1].name
            for i in six.moves.range(len(sorted_causes) - 1)
        )
        assert modified_constrains == option_1 or modified_constrains == option_2

    def test_constraints_check_basic(self):
        rule = Rule(
            [self.cause_a, self.cause_b], self.effect, [
                {
                    'clues_groups': [[0, 1], [1, 1], [2, 1]],
                    'name': 'identical',
                    'params': {}
                }
            ]
        )  # yapf: disable
        effect_clues_dict = {'effect': Clue((42,), '42 dinners', 1420, self.line_source)}
        clues = {  # it's dictionary of the same type as clues dict collected in SearchManager
            'cause_a': [
                Clue((40,), '40 carrots', 400, self.line_source),
                Clue((42,), '42 carrots', 420, self.line_source),
                Clue((44,), '44 carrots', 440, self.line_source)
            ],
            'cause_b': [
                Clue((32,), '32 broccoli', 100, self.line_source),
                Clue((42,), '42 broccoli', 120, self.line_source),
                Clue((52,), '52 broccoli', 140, self.line_source)
            ],
            'dummy': [
                Clue((42,), '42 foo bar', 980, self.line_source),
                Clue((84,), '84 foo bar', 990, self.line_source)
            ]
        }  # yapf: disable
        results = rule.constraints_check(clues, effect_clues_dict)

        assert len(results) == 1
        assert all(isinstance(cause, InvestigationResult) for cause in results)
        assert all(isinstance(line, FrontInput) for line in results[0].lines)
        assert results[0].lines == [
            Verifier._front_input_from_clue(
                Clue((42,), '42 carrots', 420, self.line_source)),
            Verifier._front_input_from_clue(
                Clue((42,), '42 broccoli', 120, self.line_source))
        ]  # yapf: disable

    def test_constraints_check_same_cause_parser_as_effect(self):
        rule = Rule(
            [self.cause_a], self.cause_a, [
                {
                    'clues_groups': [[0, 1], [1, 1]],
                    'name': 'identical',
                    'params': {}
                }
            ]
        )  # yapf: disable
        effect_clues_dict = {'cause_a': Clue((42,), '42 carrots', 1420, self.line_source)}
        clues = {  # it's dictionary of the same type as clues dict collected in SearchManager
            'cause_a': [
                Clue((40,), '40 carrots', 400, self.line_source),
                Clue((42,), '42 carrots', 420, self.line_source),
                Clue((44,), '44 carrots', 440, self.line_source)
            ],
            'dummy': [
                Clue((98,), '98 foo bar', 980, self.line_source),
                Clue((99,), '99 foo bar', 990, self.line_source)
            ]
        }  # yapf: disable
        results = rule.constraints_check(clues, effect_clues_dict)

        assert len(results) == 1
        assert all(isinstance(cause, InvestigationResult) for cause in results)
        assert all(isinstance(line, FrontInput) for line in results[0].lines)
        assert results[0].lines == [
            Verifier._front_input_from_clue(
                Clue((42,), '42 carrots', 420, self.line_source))
        ]  # yapf: disable

    def test_constraints_check_two_same_parsers(self):
        rule = Rule(
            [self.cause_a, self.cause_a], self.effect, [
                {
                    'clues_groups': [[0, 1], [1, 1], [2, 1]],
                    'name': 'identical',
                    'params': {}
                }
            ]
        )  # yapf: disable
        effect_clues_dict = {'effect': Clue((42,), '42 dinners', 1420, self.line_source)}
        clues = {  # it's dictionary of the same type as clues dict collected in SearchManager
            'cause_a': [
                Clue((40,), '40 carrots', 400, self.line_source),
                Clue((42,), '42 carrots', 420, self.line_source),
                Clue((44,), '44 carrots', 440, self.line_source),
                Clue((42,), '42 carrots', 460, self.line_source),
                Clue((40,), '40 carrots', 480, self.line_source),
            ],
            'dummy': [
                Clue((98,), '98 foo bar', 980, self.line_source),
                Clue((99,), '99 foo bar', 990, self.line_source)
            ]
        }  # yapf: disable
        results = rule.constraints_check(clues, effect_clues_dict)

        assert len(results) == 2
        assert all(isinstance(cause, InvestigationResult) for cause in results)
        assert all(isinstance(line, FrontInput) for line in results[0].lines + results[1].lines)
        assert results[0].lines == [
            Verifier._front_input_from_clue(
                Clue((42,), '42 carrots', 420, self.line_source)),
            Verifier._front_input_from_clue(
                Clue((42,), '42 carrots', 460, self.line_source))
        ]  # yapf: disable
        assert results[1].lines == [
            Verifier._front_input_from_clue(
                Clue((42,), '42 carrots', 460, self.line_source)),
            Verifier._front_input_from_clue(
                Clue((42,), '42 carrots', 420, self.line_source))
        ]  # yapf: disable

    def test_empty_clues_going_to_verify(self):
        rule = Rule(
            [self.cause_a, self.cause_a], self.effect, [
                {
                    'clues_groups': [[0, 1], [1, 1], [2, 1]],
                    'name': 'identical',
                    'params': {}
                }
            ]
        )  # yapf: disable
        effect_clues_dict = {'effect': Clue((42,), '42 dinners', 1420, self.line_source)}
        clues = {  # it's dictionary of the same type as clues dict collected in SearchManager
            'cause_a': [],
            'dummy': [
                Clue((98,), '98 foo bar', 980, self.line_source),
                Clue((99,), '99 foo bar', 990, self.line_source)
            ]
        }  # yapf: disable
        results = rule.constraints_check(clues, effect_clues_dict)
        assert not results

    def test_one_matched_line_when_two_occurrences_requested(self):
        rule = Rule(
            [self.cause_a, self.cause_a], self.effect, [
                {
                    'clues_groups': [[0, 1], [1, 1], [2, 1]],
                    'name': 'identical',
                    'params': {}
                }
            ]
        )  # yapf: disable
        effect_clues_dict = {'effect': Clue((42,), '42 dinners', 1420, self.line_source)}
        clues = {  # it's dictionary of the same type as clues dict collected in SearchManager
            'cause_a': [
                Clue((42,), '42 carrots', 420, self.line_source),
            ],
            'dummy': [
                Clue((98,), '98 foo bar', 980, self.line_source),
                Clue((99,), '99 foo bar', 990, self.line_source)
            ]
        }  # yapf: disable
        results = rule.constraints_check(clues, effect_clues_dict)
        assert effect_clues_dict['effect'].regex_parameters[0] == \
            clues['cause_a'][0].regex_parameters[0]
        assert not results
