from datetime import datetime
import dateutil.parser
import dateutil.tz


class InvestigationPlan(object):
    def __init__(self, suspected_rules, investigation_metadata):
        self._suspected_rules = suspected_rules
        self._investigation_metadata = investigation_metadata

    def get_next_investigation_step_with_log_type(self):
        return self._investigation_metadata[0]


class InvestigationStep(object):
    EARLIEST_DATE = datetime.min.replace(tzinfo=dateutil.tz.tzutc())

    def __init__(self, concatenated_parser, effect_time, earliest_cause_time=EARLIEST_DATE):
        self._concatenated_parser = concatenated_parser
        self.effect_time = InvestigationStep.add_zero_timezone(effect_time)
        self.earliest_cause_time = InvestigationStep.add_zero_timezone(earliest_cause_time)

    def is_line_in_time_range(self, line):
        parsed_date = dateutil.parser.parse(line, fuzzy=True)
        parsed_date = InvestigationStep.add_zero_timezone(parsed_date)
        return self.effect_time >= parsed_date >= self.earliest_cause_time

    @classmethod
    def add_zero_timezone(cls, date):
        if date.tzinfo is None:
            return date.replace(tzinfo=dateutil.tz.tzutc())
        return date

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
