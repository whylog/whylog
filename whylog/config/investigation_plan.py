from datetime import datetime


class InvestigationPlan(object):
    def __init__(self, suspected_rules, investigation_metadata):
        self._suspected_rules = suspected_rules
        self._investigation_metadata = investigation_metadata

    def get_next_investigation_step_with_log_type(self):
        return self._investigation_metadata[0]


class RuleSubset(object):
    def __init__(self, rule_dict):
        pass

    def get_logs_types(self):
        pass

    def get_rules_for_log_type(self, log_type):
        pass

    def get_parsers_for_log_type(self, log_type):
        pass


class InvestigationStep(object):
    def __init__(self, concatenated_parser, effect_time, earliest_cause_time):
        self._concatenated_parser = concatenated_parser
        self.effect_time = effect_time
        self.earliest_cause_time = earliest_cause_time

    # mocked Clue for second line in node_1.log for 003 test
    def mocked_clues(self):
        line_source = LineSource('localhost', 'node_1.log', 40)
        line_time = datetime(2015, 12, 3, 12, 8, 8)
        regex_parametes = {'cause': (line_time,)}
        return {
            'cause': Clue(regex_parametes, line_time, '2015-12-03 12:08:08 root cause', line_source)
        }

    def get_clues(self, line, offset):
        """
        Basing on parsers creates clues in investigation
        :param line: line from parsed file
        :returns: list of created clues
        """
        return self.mocked_clues()


class Clue(object):
    """
    Collects all the data that parser can extract from single log line.
    Also, contains parsed line and its source.
    """

    def __init__(self, regex_parameters, line_time, line_prefix_content, line_source):
        pass


class LineSource(object):
    def __init__(self, host, path, offset):
        self.host = host
        self.path = path
        self.offset = offset
