import itertools


class InvestigationUtils(object):
    @classmethod
    def merge_clue_dicts(cls, collector, clues_dict):
        for parser_name, clues_list in clues_dict.items():
            collector[parser_name] = itertools.chain(collector[parser_name], clues_list)
