from unittest import TestCase

from whylog.config.investigation_plan import Clue, LineSource
from whylog.config.parsers import RegexParser
from whylog.config.rule import Rule
from whylog.constraints.verifier import InvestigationResult, Verifier
from whylog.front import FrontInput


class TestBasic(TestCase):
    cause_a = RegexParser('cause_a', '31 carrots', '^(\d\d) carrots$', [1], 'default', {1: 'int'})
    cause_b = RegexParser('cause_b', '79 broccoli', '^(\d\d) broccoli$', [1], 'default', {1: 'int'})
    effect = RegexParser('effect', '53 dinners', '^(\d\d) carrots$', [1], 'default', {1: 'int'})
    line_source = LineSource('localhost', 'node_1.log')

    def test_constraints_check_basic(self):
        rule = Rule(
            [TestBasic.cause_a, TestBasic.cause_b], TestBasic.effect, [
                {
                    'clues_groups': [[0, 1], [1, 1], [2, 1]],
                    'name': 'identical',
                    'params': {}
                }
            ]
        )  # yapf: disable
        effect_clues_dict = {'effect': Clue((42,), '42 dinners', 1420, TestBasic.line_source)}
        clues = {  # it's dictionary of the same type as clues dict collected in SearchManager
            'cause_a': [
                Clue((40,), '40 carrots', 400, TestBasic.line_source),
                Clue((42,), '42 carrots', 420, TestBasic.line_source),
                Clue((44,), '44 carrots', 440, TestBasic.line_source)
            ],
            'cause_b': [
                Clue((32,), '32 broccoli', 100, TestBasic.line_source),
                Clue((42,), '42 broccoli', 120, TestBasic.line_source),
                Clue((52,), '52 broccoli', 140, TestBasic.line_source)
            ],
            'dummy': [
                Clue((98,), '98 foo bar', 980, TestBasic.line_source),
                Clue((99,), '99 foo bar', 990, TestBasic.line_source)
            ]
        }  # yapf: disable
        results = rule.constraints_check(clues, effect_clues_dict)

        assert len(results) == 1
        assert all(isinstance(cause, InvestigationResult) for cause in results)
        assert all(isinstance(line, FrontInput) for line in results[0].lines)
        assert results[0].lines == [
            Verifier._front_input_from_clue(
                Clue((42,), '42 carrots', 420, TestBasic.line_source)),
            Verifier._front_input_from_clue(
                Clue((42,), '42 broccoli', 120, TestBasic.line_source))
        ]  # yapf: disable

    def test_constraints_check_same_cause_parser_as_effect(self):
        rule = Rule(
            [TestBasic.cause_a], TestBasic.cause_a, [
                {
                    'clues_groups': [[0, 1], [1, 1]],
                    'name': 'identical',
                    'params': {}
                }
            ]
        )  # yapf: disable
        effect_clues_dict = {'cause_a': Clue((42,), '42 carrots', 1420, TestBasic.line_source)}
        clues = {  # it's dictionary of the same type as clues dict collected in SearchManager
            'cause_a': [
                Clue((40,), '40 carrots', 400, TestBasic.line_source),
                Clue((42,), '42 carrots', 420, TestBasic.line_source),
                Clue((44,), '44 carrots', 440, TestBasic.line_source)
            ],
            'dummy': [
                Clue((98,), '98 foo bar', 980, TestBasic.line_source),
                Clue((99,), '99 foo bar', 990, TestBasic.line_source)
            ]
        }  # yapf: disable
        results = rule.constraints_check(clues, effect_clues_dict)

        assert len(results) == 1
        assert all(isinstance(cause, InvestigationResult) for cause in results)
        assert all(isinstance(line, FrontInput) for line in results[0].lines)
        assert results[0].lines == [
            Verifier._front_input_from_clue(
                Clue((42,), '42 carrots', 420, TestBasic.line_source))
        ]  # yapf: disable
