import six

from whylog.config.utils import CompareResult


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
    LEFT_BOUND, RIGHT_BOUND = 0, 1

    def __init__(self, parser_subset, search_ranges):
        self._parser_subset = parser_subset
        self._search_ranges = search_ranges

    def is_line_in_search_range(self, super_parser_groups):
        #TODO: delete this deprecated method
        return True

    def compare_with_bound(self, bound, super_parser_groups):
        """
        Basing on super_parser_groups extracted from line, returns information
        how relative to choosed bound (LEFT_BOUND or RIGHT_BOUND) this line is.
        Example:
            bound = InvestigationStep.LEFT_BOUND (only other possible value of this parameter is
                    InvestigationStep.RIGHT_BOUND)
            super_parser_groups = [('date', datetime(2015, 12, 3, 12, 8, 9))]
            self._search_ranges = {
                'date': {
                    'left_bound': datetime(2015, 12, 3, 12, 8, 0),
                    'right_bound': datetime(2015, 12, 3, 12, 8, 11)
                }
            }
            returned value: CompareResult.GT
        When self._search_ranges hasn't defined bounds for given primary key type this method
        return GT/LT when compare with RIGHT_BOUND/LEFT_BOUND.
        This means that InvestigationStep object hasn't information about order in parsed file.
        """
        # This implementation assume that super_parser_groups length equals 1 or 0
        # TODO implementation for longer super_parser_groups_list
        group_value, bound_value = self._extract_values_to_compare(bound, super_parser_groups)
        if bound_value is None:
            return self._compare_with_undefined_bound(bound)
        return self._compare_values(bound_value, group_value)

    def _extract_values_to_compare(self, bound, super_parser_groups):
        if not super_parser_groups:
            return None, None
        group_type, group_value = super_parser_groups[0]
        # type_bound is a dictionary, that contains bounds (LEFT and RIGHT bound)
        # values for concrete primary key type
        type_bounds = self._search_ranges.get(group_type)
        if type_bounds is None:
            return None, None
        return group_value, type_bounds[bound]

    def _compare_with_undefined_bound(self, bound):
        if bound == self.LEFT_BOUND:
            return CompareResult.GT
        return CompareResult.LT

    @classmethod
    def _compare_values(cls, bound_value, group_value):
        if group_value < bound_value:
            return CompareResult.LT
        elif group_value > bound_value:
            return CompareResult.GT
        return CompareResult.EQ

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
        return all((
            self.regex_parameters == other.regex_parameters,
            self.line_prefix_content == other.line_prefix_content,
            self.line_offset == other.line_offset,
            self.line_source == other.line_source
        ))  # yapf: disable


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

    def __hash__(self):
        return hash(self.host + self.path)
