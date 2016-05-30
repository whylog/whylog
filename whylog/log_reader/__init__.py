import itertools
from abc import ABCMeta, abstractmethod
from collections import defaultdict

import six
from frozendict import frozendict

from whylog.log_reader.exceptions import NoLogTypeError
from whylog.log_reader.investiagtion_utils import InvestigationUtils
from whylog.log_reader.searchers import BacktrackSearcher

EMPTY_FROZEN_DICT = frozendict()


@six.add_metaclass(ABCMeta)
class AbstractLogReader(object):
    @abstractmethod
    def get_causes(self, front_input):
        pass

    @abstractmethod
    def get_causes_tree(self, front_input):
        pass


class LogReader(AbstractLogReader):
    def __init__(self, config):
        self.config = config

    def get_causes(self, front_input, tmp_assign_to_log_type=EMPTY_FROZEN_DICT):
        input_line_source = front_input.line_source
        input_log_type = self._get_input_log_type(tmp_assign_to_log_type, input_line_source) or \
                         self.config.get_log_type(input_line_source)
        if not input_log_type:
            raise NoLogTypeError(input_line_source)
        investigation_plan = self.config.create_investigation_plan(front_input, input_log_type)
        manager = SearchManager(investigation_plan)
        return manager.investigate(front_input, tmp_assign_to_log_type)

    @classmethod
    def _get_input_log_type(cls, tmp_assign_to_log_type, input_line_source):
        for log_type, line_sources in six.iteritems(tmp_assign_to_log_type):
            if input_line_source in line_sources:
                return log_type

    def get_causes_tree(self, front_input):
        pass


class SearchManager(object):
    def __init__(self, investigation_plan):
        self._investigation_plan = investigation_plan

    @classmethod
    def _save_clues_in_normal_dict(cls, collector):
        return dict(
            (parser_name, list(clues_iter)) for parser_name, clues_iter in six.iteritems(collector)
        )

    def _constraints_verification(self, clues):
        """
        provides constraints verification basing on
        rules from investigation_plan and collected clues
        """
        causes = []
        for rule in self._investigation_plan.suspected_rules:
            results_from_rule = rule.constraints_check(clues, self._investigation_plan.effect_clues)
            causes.extend(results_from_rule)
        return causes

    def investigate(self, original_front_input, tmp_assign_to_log_type=EMPTY_FROZEN_DICT):
        """
        this function collects clues from SearchHandlers
        (each of them corresponds to one InvestigationStep)
        in dictionary clues_collector
        and then provide their verification with constraints
        :return: list of InvestigationResults
        """
        clues_collector = defaultdict(itertools.chain)
        for step, log_type in self._investigation_plan.investigation_steps_with_log_types:
            search_handler = SearchHandler(step, log_type)
            InvestigationUtils.merge_clue_dicts(
                clues_collector, search_handler.investigate(
                    original_front_input, tmp_assign_to_log_type.get(log_type)
                )
            )
        clues = self._save_clues_in_normal_dict(clues_collector)
        return self._constraints_verification(clues)


class SearchHandler(object):
    def __init__(self, investigation_step, log_type):
        self._investigation_step = investigation_step
        self._log_type = log_type

    def investigate(self, original_front_input, forced_log_type=None):
        clues = defaultdict(itertools.chain)
        for host, path, super_parser in self._log_type.files_to_parse(forced_log_type):
            if host == "localhost":
                searcher = BacktrackSearcher(path, self._investigation_step, super_parser)
                InvestigationUtils.merge_clue_dicts(clues, searcher.search(original_front_input))
            else:
                raise NotImplementedError(
                    "Cannot operate on %s which is different than %s" % (host, "localhost")
                )
        return clues
