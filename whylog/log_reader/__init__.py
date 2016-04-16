import itertools
from abc import ABCMeta, abstractmethod

import six

from whylog.front import FrontInput
from whylog.log_reader.exceptions import NoLogTypeError
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
    def _merge_dicts(cls, collector, clue_dict):
        for parser_name, clues_list in clue_dict.items():
            if parser_name in collector:
                collector[parser_name] = itertools.chain(collector[parser_name], clues_list)
            else:
                collector[parser_name] = itertools.chain(clue_dict[parser_name])

    @classmethod
    def _save_clues_in_normal_dict(cls, collector):
        standard_dict = {}
        for parser_name, clues_list in collector.items():
            standard_dict[parser_name] = list(clues_list)
        return standard_dict

    def investigate(self):
        clues_collector = {}
        for step, log_type in self._investigation_plan.get_next_investigation_step_with_log_type():
            search_handler = SearchHandler(step, log_type)
            self._merge_dicts(clues_collector, search_handler.investigate())
        # clues = self._save_clues_in_normal_dict(clues_collector)
        # TODO checking up the constraints should take place here
        return [
            FrontInput(
                69, "2015-12-03 12:08:08 root cause", "node_1.log"
            )
        ]  # TODO it's a mock! values should be returned basing on clues and constraints


class SearchHandler(object):
    def __init__(self, investigation_step, log_type):
        self._investigation_step = investigation_step
        self._log_type = log_type

    @classmethod
    def _merge_clue_dicts(cls, collector, dict_with_lists):
        for parser_name, clues_list in dict_with_lists.items():
            if parser_name in collector:
                collector[parser_name] = itertools.chain(collector[parser_name], clues_list)
            else:
                collector[parser_name] = itertools.chain(dict_with_lists[parser_name])

    def investigate(self):
        clues = {}
        for host, path in self._log_type.get_next_file_to_parse():
            if host == "localhost":
                searcher = BacktrackSearcher(path)
                self._merge_clue_dicts(clues, searcher.search(self._investigation_step))
            else:
                raise NotImplementedError(
                    "Cannot operate on %s which is different than %s" % (host, "localhost")
                )
        return clues
