from abc import ABCMeta, abstractmethod

import six

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
        investigation_plan = self.config.create_investigation_plan(front_input)
        if not investigation_plan:
            return None  # TODO information about no investigation plan must somehow be returned to
            # the front-module - we need more data to provide the investigation
            # if we have the investigation plan, we can begin the investigation
        manager = SearchManager(investigation_plan)
        return manager.investigate()

    def get_causes_tree(self, front_input):
        pass


class SearchManager(object):
    def __init__(self, investigation_plan):
        self._investigation_plan = investigation_plan

    def investigate(self):
        """
        :rtype: InvestigationResult
        """
        for step in self._investigation_plan.get_step():
            search_handler = SearchHandler(step)
            # TODO where checking up the constraints should take place?
            clues = search_handler.investigate()
        return InvestigationResult()  # TODO of course return something with sense


class SearchHandler(object):
    def __init__(self, investigation_step):
        self._investigation_step = investigation_step

    def investigate(self):
        clues = []
        # TODO where checking up the constraints should take place?
        for host, file_path in self._investigation_step.get_data():
            searcher = BacktrackSearcher(file_path)
            clues += searcher.search(self._investigation_step)  # TODO on what data it should be called?
        return clues  # TODO of course return something with sense


class InvestigationResult(object):
    pass  # TODO discuss with Front what should be returned and in what form
