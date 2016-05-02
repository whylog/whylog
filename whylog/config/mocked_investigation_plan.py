from datetime import datetime

from whylog.config.filename_matchers import WildCardFilenameMatcher
from whylog.config.investigation_plan import Clue, InvestigationPlan, InvestigationStep, LineSource
from whylog.config.log_type import LogType
from whylog.config.parser_subset import ConcatenatedRegexParser
from whylog.config.parsers import RegexParser
from whylog.config.rule import Rule


# mocked investigation plan for 003_match_time_range test
# TODO: remove mock
def mocked_investigation_plan():
    matcher = WildCardFilenameMatcher('localhost', 'node_1.log', 'default')
    default_log_type = LogType('default', [matcher])
    cause = RegexParser(
        'cause', '2015-12-03 12:08:08 root cause',
        '^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) root cause$', [1], 'default', {1: 'date'}
    )
    effect = RegexParser(
        'effect', '2015-12-03 12:08:09 visible effect',
        '^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) visible effect$', [1], 'default', {1: 'date'}
    )
    concatenated = ConcatenatedRegexParser([cause])
    effect_time = datetime(2015, 12, 3, 12, 8, 9)
    earliest_cause_time = datetime(2015, 12, 3, 12, 8, 8)
    default_investigation_step = InvestigationStep(concatenated, effect_time, earliest_cause_time)
    rule = Rule(
        [cause], effect, [
            {
                'clues_groups': [[1, 1], [0, 1]],
                'name': 'time',
                'params': {'max_delta': 1}
            }
        ]
    )  # yapf: disable
    line_source = LineSource('localhost', 'node_1.log')
    effect_clues = {'effect': Clue((effect_time,), 'visible effect', 40, line_source)}
    return InvestigationPlan([rule], [(default_investigation_step, default_log_type)], effect_clues)
