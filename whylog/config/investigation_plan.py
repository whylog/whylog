import six


class InvestigationPlan(object):
    """
    Represents all rules that can be fulfilled in single investigation.
    Also contains all investigation metadata, what means all pairs
    (investigationstep, logtype) neccesary for investigation
    For single log type we have single investigation step.
    """

    def __init__(self, suspected_rules, investigation_metadata, effect_clues):
        self._suspected_rules = suspected_rules
        self._investigation_metadata = investigation_metadata
        self._effect_clues = effect_clues

    @property
    def investigation_steps_with_log_types(self):
        return self._investigation_metadata

    @property
    def suspected_rules(self):
        return self._suspected_rules

    @property
    def effect_clues(self):
        return self._effect_clues


class InvestigationStep(object):
    """
    Contains all parsers for single log type that can be matched in actual investigation.
    This class is responsible for finding all possible Clues from parsed logs.
    Also controls searched time range in logs file.
    """
    def __init__(self, parser_subset, search_ranges):
        self._parser_subset = parser_subset
        self._search_ranges = search_ranges

    def is_line_in_search_range(self, super_parser_groups):
        #TODO: write method that check that line is in primary key values range
        return True

    def get_clues(self, line, offset, line_source):
        converted_params = self._parser_subset.convert_parsers_groups_from_matched_line(line)
        return dict(
            (parser_name, Clue(converted_groups, line, offset, line_source))
            for parser_name, converted_groups in six.iteritems(converted_params)
        )


class Clue(object):
    """
    Collects all the data that parser subset can extract from single log line.
    Also, contains parsed line and its source.
    """

    def __init__(self, regex_parameters, line_prefix_content, line_offset, line_source):
        self.regex_parameters = regex_parameters
        self.line_prefix_content = line_prefix_content
        self.line_offset = line_offset
        self.line_source = line_source

    def __repr__(self):
        if all(
            elem is None
            for elem in [
                self.regex_parameters, self.line_prefix_content, self.line_offset, self.line_source
            ]
        ):
            return "(Clue: UNMATCHED)"
        return "(Clue: %s, %s, %s, %s)" % (
            self.regex_parameters, self.line_prefix_content, self.line_offset, self.line_source
        )

    def __eq__(self, other):
        return all([
            self.regex_parameters == other.regex_parameters,
            self.line_prefix_content == other.line_prefix_content,
            self.line_offset == other.line_offset,
            self.line_source == other.line_source
        ])  # yapf: disable


class LineSource(object):
    def __init__(self, host, path):
        self.host = host
        self.path = path

    def __repr__(self):
        return "(LineSource: %s:%s)" % (self.host, self.path)

    def __eq__(self, other):
        if other is None:
            return False
        return all((self.host == other.host, self.path == other.path))
