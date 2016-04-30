import itertools
import six


class InvestigationUtils(object):
    @classmethod
    def merge_clue_dicts(cls, collector, clues_dict):
        for parser_name, clues_list in six.iteritems(clues_dict):
            collector[parser_name] = itertools.chain(collector[parser_name], clues_list)
