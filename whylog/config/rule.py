import itertools
from abc import ABCMeta, abstractmethod
from collections import defaultdict, deque

import six
from frozendict import frozendict

from whylog.config.investigation_plan import InvestigationStep
from whylog.config.parsers import RegexParserFactory
from whylog.constraints.constraint_manager import ConstraintManager
from whylog.constraints.verifier import Verifier
from whylog.converters import CONVERTION_MAPPING


class Rule(object):
    EMPTY_BLACK_LIST = frozenset()
    LINKAGE_AND = "AND"
    LINKAGE_OR = "OR"
    LINKAGE_NOT = "NOT"

    LINKAGE_SELECTOR = {
        LINKAGE_AND: Verifier.constraints_and,
        LINKAGE_OR: Verifier.constraints_or,
        LINKAGE_NOT: Verifier.constraints_not
    }

    EFFECT_NUMBER = 0
    NO_RANGE = frozendict()
    DELTA_CONSTRAINTS = set(['time'])

    def __init__(self, causes, effect, constraints, linkage):
        self._causes = causes
        self._effect = effect
        self._constraints = constraints
        self._linkage = linkage
        self._frequency_information = self._gather_causes_frequency_information()

    def _gather_causes_frequency_information(self):
        """
        basing on self._causes and assumption that causes are sorted,
        produces list of pairs: (parser name, number of occurrences of this parser)
        """
        return [(elem.name, len(list(group))) for elem, group in itertools.groupby(self._causes)]

    def serialize(self):
        return {
            "causes": [
                cause.name for cause in self._causes
            ],
            "effect": self._effect.name,
            "constraints": self._constraints,
        }

    def get_new_parsers(self, parser_name_generator):
        new_parsers = []
        for parser in itertools.chain([self._effect], self._causes):
            # TODO: Refactor if teachers are mulithreding
            if parser_name_generator.is_free_parser_name(parser.name, self.EMPTY_BLACK_LIST):
                new_parsers.append(parser)
        return new_parsers

    def get_causes_parsers(self):
        return self._causes

    def get_effect_name(self):
        return self._effect.name

    def get_search_ranges(self, effect_clues):
        """
        parser's search range is a dictionary with search range for its primary key type:
        Sample parser's search range:
        {
            'date': {
                InvesitgationStep.LEFT_BOUND: datetime(2016, 5, 29, 12, 33, 0),
                InvesitgationStep.RIGHT_BOUND: datetime(2016, 5, 29, 12, 33, 30)
            }
        }
        This method calculate search ranges for single rule based on its
        constraints and effect clues.
        Algorithm steps:
            1. Check that effect parser has no empty primary key. If is empty
             return NO_RANGE
            2. Calculate search range for every cause parser.
            3. Join parsers search ranges with this same log type
        """
        group_number, group_type = self._effect.get_primary_key_group()
        if not group_number:
            return self.NO_RANGE
        parser_ranges = self._calculate_parsers_ranges(effect_clues, group_number, group_type)
        if self._linkage == self.LINKAGE_OR:
            self._update_parser_ranges_with_or_linkage(
                effect_clues, group_number, group_type, parser_ranges
            )
        return self._aggregate_by_log_type(parser_ranges)

    def _calculate_parsers_ranges(self, effect_clues, group, group_type):
        """
        This method calculate search range for every cause parser in rule.
        This algorithm working only on delta constraints these allow reasoning about
        parser's search range.
        Delta constraints analysis:
            Such constraint contains clues_groups list that contains two elements. Each of
            elements is a two element list.
            For example:
                clues_groups = [[1,1], [0,1]]
                It means that first group of first parser depend to first group o zero parser.
                If these first groups of these parsers are in primary keys, we can predict
                first parser search ranges basing on zero parser search range.
                Assume that:
                params = { min_delta: 10, max_delta: 100}
                zero parser search ranges = {'int': {LEFT_BOUND: 200, RIGHT_BOUND: 250}
                then
                first parser search range = {'int': {LEFT_BOUND: 200 - 100, RIGHT_BOUND: 250 - 10}
                In code first parser calls depended parser, zero parser calls base parser.
        Connectivity parsers graph is directed graph were two parsers from rule are connected when
        are connected by delta constraint. This edge is directed from base to depended parser.
        This implementation assume that connectivity parsers graph is a tree.
        Algorithm steps:
            1. Calculate effect parser search range. Take primary key values from effect_clues.
            2. For every parser in rule find its all delta constraints where is a base parser
                (_aggregate_constraints method). It is connectivity parsers graph creator.
            3. Do a BFS order over connectivity parsers graph. Start from effect parser which is a root in tree.
                Calculate parser search range for every child parser of actual parser if it is possible.
            4. Set maximal search range for all unreachable parser from effect parser in graph
            5. Pop effect parser search range.
        """
        parser_ranges = {
            self.EFFECT_NUMBER: self._get_effect_range(effect_clues, group, group_type)
        }
        queue = deque([self.EFFECT_NUMBER])
        aggregated_constraints = self._aggregate_constraints()
        used_parsers = set([self.EFFECT_NUMBER])
        while queue:
            parser_number = queue.popleft()
            for constraint in aggregated_constraints[parser_number]:
                clues_groups = constraint['clues_groups']
                depended_parser_number = clues_groups[0][0]
                base_parser_number = clues_groups[1][0]
                if depended_parser_number in used_parsers:
                    continue
                if not self._is_primary_key_constraint(clues_groups):
                    continue
                _, group_type = self._causes[depended_parser_number - 1].get_primary_key_group()
                parser_ranges[depended_parser_number] = self._calculate_parser_bounds(
                    base_parser_number, constraint['params'], group_type, parser_ranges
                )
                queue.append(depended_parser_number)
                used_parsers.add(depended_parser_number)
        self.create_ranges_for_unconnected_parsers(effect_clues, group, group_type, parser_ranges)
        parser_ranges.pop(self.EFFECT_NUMBER)
        return parser_ranges

    def _get_effect_range(self, effect_clues, group_number, group_type):
        """
        This method basing on effect clues and effect primary key creates effect
        search range for effect primary key type which in LEFT_BOUND = RIGHT_BOUND and equals
        primary key value from effect clues.
        This method is invokes when algorithm with calculate parsers ranges starts. It give
        set up for this algorithm.
        Example:
            clues_groups = {'effect' : Clue((11, 'aaa'), '11 aaa', LineSource('foo', 'bar'))}
            group_number = 1
            group_type = 'int'
            expected returned value : {EFFECT_NUMBER: {'int': {LEFT_BOUND: 11, RIGHT_BOUND: 11}}}
        """
        # Here assumption that len of primary_keys_groups equals 1
        primary_group_value = effect_clues[self.get_effect_name()].regex_parameters[group_number - 1] # yapf: disable
        return {
            group_type: {
                InvestigationStep.LEFT_BOUND: primary_group_value,
                InvestigationStep.RIGHT_BOUND: primary_group_value
            }
        }

    def _aggregate_constraints(self):
        """
        This method groups delta constraints by equal base parser
        """
        parser_with_constraints = defaultdict(list)
        for constraint in self._constraints:
            if constraint['name'] in self.DELTA_CONSTRAINTS:
                base_parser = constraint['clues_groups'][1][0]
                parser_with_constraints[base_parser].append(constraint)
        return parser_with_constraints

    def _is_primary_key_constraint(self, clues_groups):
        """
        This method checks that groups connected by delta constraint belongs to primary key
        """
        base_parser_number = clues_groups[1][0]
        depended_parser_number = clues_groups[0][0]
        base_parser_group_number = clues_groups[1][1]
        depended_group_number = clues_groups[0][1]
        return self._is_group_primary(base_parser_group_number, base_parser_number) and \
               self._is_group_primary(depended_group_number, depended_parser_number)

    def _is_group_primary(self, parser_group_number, parser_number):
        if parser_number == self.EFFECT_NUMBER:
            return self._effect.is_primary_key(parser_group_number)
        return self._causes[parser_number - 1].is_primary_key(parser_group_number)

    def _calculate_parser_bounds(self, base_parser_number, params, group_type, parser_ranges):
        """
        This method calculate depended parser search range basing od base parser search range.
        """
        max_delta = params.get('max_delta')
        min_delta = params.get('min_delta')
        left_bound, right_bound = self._get_base_bounds(
            base_parser_number, group_type, parser_ranges
        )
        converter = CONVERTION_MAPPING[group_type]
        new_left_bound = converter.switch_by_delta(left_bound, max_delta, "max")
        new_right_bound = converter.switch_by_delta(right_bound, min_delta, "min")
        return {
            group_type: {
                InvestigationStep.LEFT_BOUND: new_left_bound,
                InvestigationStep.RIGHT_BOUND: new_right_bound
            }
        }

    @classmethod
    def _get_base_bounds(cls, base_parser_number, group_type, parser_ranges):
        base_parser_bounds = parser_ranges[base_parser_number][group_type]
        left_bound = base_parser_bounds[InvestigationStep.LEFT_BOUND]
        right_bound = base_parser_bounds[InvestigationStep.RIGHT_BOUND]
        return left_bound, right_bound

    def create_ranges_for_unconnected_parsers(
        self, effect_clues, effect_primary_group, effect_group_type, parser_ranges
    ):
        """
        Create maximal search range for parsers which are unreachable by delta constraints.
        """
        effect_primary_group_value = effect_clues[self.get_effect_name(
        )].regex_parameters[effect_primary_group - 1]
        for i in six.moves.range(len(self._causes)):
            if (i + 1) not in parser_ranges:
                _, primary_group_type = self._causes[i].get_primary_key_group()
                converter = CONVERTION_MAPPING[primary_group_type]
                right_bound = converter.MAX_VALUE
                if primary_group_type == effect_group_type:
                    right_bound = effect_primary_group_value
                parser_ranges[(i + 1)] = {
                    primary_group_type: {
                        InvestigationStep.LEFT_BOUND: converter.MIN_VALUE,
                        InvestigationStep.RIGHT_BOUND: right_bound
                    }
                }

    def _update_parser_ranges_with_or_linkage(
        self, effect_clues, effect_group, effect_group_type, parser_ranges
    ):
        """
        This method updates parsers ranges, when rule constraints are connected
        by OR linkage to maximal possibly range. If we find constraint that hasn't delta we can't
        limit parser's search ranges for all parser connected by this constraint.
        """
        effect_group_value = \
            effect_clues[self.get_effect_name()].regex_parameters[effect_group - 1]
        for constraint in self._constraints:
            if constraint['name'] in self.DELTA_CONSTRAINTS:
                continue
            for clue_group in constraint['clues_groups']:
                parser_number = clue_group[0]
                if parser_number == self.EFFECT_NUMBER:
                    continue
                _, primary_group_type = self._causes[parser_number - 1].get_primary_key_group()
                converter = CONVERTION_MAPPING[primary_group_type]
                new_right_bound = converter.MAX_VALUE
                if primary_group_type == effect_group_type:
                    new_right_bound = effect_group_value
                primary_group_type_bound = parser_ranges[parser_number][primary_group_type]
                primary_group_type_bound[InvestigationStep.RIGHT_BOUND] = new_right_bound
                primary_group_type_bound[InvestigationStep.LEFT_BOUND] = converter.MIN_VALUE

    def _aggregate_by_log_type(self, parsers_ranges):
        """
        This method joins parser's search ranges belongs to single
        log type. LEFT_BOUND of primary key type from log type is a
        minimum of all LEFT_BOUND from parsers has a this primary key type belongs
        to this log type. Similarly for RIGHT_BOUND takes maximum over parsers RIGHT_BOUND
        Example:
            parsers_ranges = {
                1: {
                    'int' : { LEFT_BOUND: 10, RIGHT_BOUND: 20}
                },
                2: {
                    'int' : { LEFT_BOUND: 5, RIGHT_BOUND: 30}
                },
                3: {
                    'int' : {LEFT_BOUND: 30, RIGHT_BOUND: 40}
                }
            }
            where 1 and 2 parser belongs to apache log type, but
            3 belongs to database log type
            expected returned value: {
                'apache' : {'int': {LEFT_BOUND: 5, RIGHT_BOUND: 30}},
                'database': {'int': {LEFT_BOUND: 30, RIGHT_BOUND: 40}}
            }
        """
        search_ranges = {}
        for parser_number, ranges in six.iteritems(parsers_ranges):
            parser_log_type = self._causes[parser_number - 1].log_type
            if parser_log_type not in search_ranges:
                search_ranges[parser_log_type] = ranges
                continue
            self._update_log_type_ranges(parser_log_type, ranges, search_ranges)
        return search_ranges

    @classmethod
    def _update_log_type_ranges(cls, parser_log_type, ranges, search_ranges):
        for group_type in ranges:
            if group_type not in search_ranges[parser_log_type]:
                search_ranges[parser_log_type][group_type] = ranges[group_type]
                continue
            cls._update_bounds(search_ranges[parser_log_type][group_type], ranges[group_type])

    @classmethod
    def _update_bounds(cls, bounds, update_bounds):
        bounds[InvestigationStep.LEFT_BOUND] = min(
            bounds[InvestigationStep.LEFT_BOUND], update_bounds[InvestigationStep.LEFT_BOUND]
        )
        bounds[InvestigationStep.RIGHT_BOUND] = max(
            bounds[InvestigationStep.RIGHT_BOUND], update_bounds[InvestigationStep.RIGHT_BOUND]
        )

    def constraints_check(self, clues, effect_clues_dict):
        """
        check if given clues satisfy rule
        basing on its causes, effect and constraints.
        returns list of InvestigationResult objects
        """
        clues_lists = [
            (clues[parser_name], occurrences)
            for parser_name, occurrences in self._frequency_information
            if clues.get(parser_name) is not None
        ]
        effect_clue = effect_clues_dict[self._effect.name]
        constraint_manager = ConstraintManager()
        return self.LINKAGE_SELECTOR[self._linkage](
            clues_lists, effect_clue, self._constraints, constraint_manager
        )


@six.add_metaclass(ABCMeta)
class AbstractRuleFactory(object):
    @classmethod
    def create_from_intent(cls, user_rule_intent):
        parsers_dict = cls._create_parsers_from_intents(user_rule_intent)
        effect = parsers_dict.pop(user_rule_intent.effect_id)
        causes, parser_ids_mapper = cls._create_causes_list_with_clue_index(
            parsers_dict, user_rule_intent
        )
        constraints = cls._create_constraints_list(parser_ids_mapper, user_rule_intent)
        ordered_causes, modified_constraints = cls._order_causes_list(causes, constraints)
        # TODO use user_rule_intent instead of Rule.LINKAGE_AND when UserRuleIntent will support rule linkage
        return Rule(ordered_causes, effect, modified_constraints, Rule.LINKAGE_AND)

    @classmethod
    def _order_causes_list(cls, causes, constraints):
        causes_with_indexes = list(enumerate(causes, 1))
        causes_with_indexes.sort(key=lambda x: x[1].name)
        ordered_causes = []
        parser_index_mapping = {}
        for new_idx, (old_index, parser) in enumerate(causes_with_indexes, 1):
            ordered_causes.append(parser)
            parser_index_mapping[old_index] = new_idx
        for constraint in constraints:
            for clue_group in constraint['clues_groups']:
                if clue_group[0] != 0:
                    clue_group[0] = parser_index_mapping[clue_group[0]]
        return ordered_causes, constraints

    @classmethod
    @abstractmethod
    def _create_parsers_from_intents(cls, user_rule_intent):
        pass

    @classmethod
    def _create_causes_list_with_clue_index(cls, parsers_dict, user_rule_intent):
        parser_ids_mapper = {user_rule_intent.effect_id: 0}
        free_clue_index = 1
        causes = []
        for intent_id, parser in six.iteritems(parsers_dict):
            causes.append(parser)
            parser_ids_mapper[intent_id] = free_clue_index
            free_clue_index += 1
        return causes, parser_ids_mapper

    @classmethod
    def _create_constraints_list(cls, parser_ids_mapper, user_rule_intent):
        constraints = []
        for constraint_intent in user_rule_intent.constraints:
            clues = []
            for parser_id, group in constraint_intent.groups:
                cause_id = parser_ids_mapper[parser_id]
                clues.append([cause_id, group])
            constraint_dict = {
                "name": constraint_intent.type,
                "clues_groups": clues,
                "params": constraint_intent.params
            }
            constraints.append(constraint_dict)
        return constraints

    @classmethod
    def from_dao(cls, serialized_rule, parsers):
        # TODO: restore serialized_rule["linkage"] when UserRuleIntent will support rule linkage
        causes = [parsers[cause] for cause in serialized_rule["causes"]]
        return Rule(
            causes, parsers[serialized_rule["effect"]], serialized_rule["constraints"],
            serialized_rule.get("linkage", Rule.LINKAGE_AND)
        )


class RegexRuleFactory(AbstractRuleFactory):
    @classmethod
    def _create_parsers_from_intents(cls, user_rule_intent):
        return dict(
            (intent_id, RegexParserFactory.create_from_intent(parser_intent))
            for intent_id, parser_intent in six.iteritems(user_rule_intent.parsers)
        )
