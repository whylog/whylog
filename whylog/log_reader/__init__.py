import itertools
from abc import ABCMeta, abstractmethod
from collections import defaultdict

import six

from whylog.constraints import TimeConstraint
from whylog.front import FrontInput
from whylog.log_reader.exceptions import NoLogTypeError
from whylog.log_reader.investiagtion_utils import InvestigationUtils
from whylog.log_reader.searchers import BacktrackSearcher


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

    def get_causes(self, front_input):
        input_log_type = self.config.get_log_type(front_input)
        if not input_log_type:
            raise NoLogTypeError(front_input)
        investigation_plan = self.config.create_investigation_plan(front_input, input_log_type)
        manager = SearchManager(investigation_plan)
        return manager.investigate()

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
        provides constraints verification basing on rules from investigation_plan
        and collected clues
        """
        causes = []
        # effect_clues are accessible from investigation_plan._effect_clues
        for rule in self._investigation_plan._suspected_rules:
            # FIXME eliminate protected field access
            for cause in rule._causes:
                # FIXME eliminate protected field access
                if cause.name in clues:
                    for clue in clues[cause.name]:
                        for constraint in rule._constraints:
                            # TODO somehow it must be decided which constraint it is and method verify must be invoked
                            # ConstraintsBase.all[constraint['name']].verify(effect, cause, constraint)
                            # FIXME NOW I assume, that constraint['name'] == 'time'
                            if TimeConstraint.verify(rule._effect, cause, constraint):
                                causes.append(
                                    FrontInput(
                                        clue.line_source.offset, clue.line_prefix_content,
                                        clue.line_source.path
                                    )
                                )
        return causes

    def investigate(self):
        """
        this function collects clues from SearchHandlers
        (each of them corresponds to one InvestigationStep)
        in dictionary clues_collector
        and then provide their verification with constraints
        :return: list of FrontInput objects
        """
        clues_collector = defaultdict(itertools.chain)
        for step, log_type in self._investigation_plan.get_next_investigation_step_with_log_type():
            search_handler = SearchHandler(step, log_type)
            InvestigationUtils.merge_clue_dicts(clues_collector, search_handler.investigate())
        clues = self._save_clues_in_normal_dict(clues_collector)
        return self._constraints_verification(clues)


class SearchHandler(object):
    def __init__(self, investigation_step, log_type):
        self._investigation_step = investigation_step
        self._log_type = log_type

    def investigate(self):
        clues = defaultdict(itertools.chain)
        for host, path in self._log_type.files_to_parse():
            if host == "localhost":
                searcher = BacktrackSearcher(path)
                InvestigationUtils.merge_clue_dicts(
                    clues, searcher.search(self._investigation_step)
                )
            else:
                raise NotImplementedError(
                    "Cannot operate on %s which is different than %s" % (host, "localhost")
                )
        return clues
