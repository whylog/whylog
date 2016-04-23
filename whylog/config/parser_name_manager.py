import re

WORDS_IN_NAME = 2


class ParserNameManager(object):
    def __init__(self, parsers):
        self._parsers_name = set()
        for parser_name in parsers:
            self._parsers_name.add(parser_name)

    def add_new_parser_name(self, parser_name):
        self._parsers_name.add(parser_name)

    def is_free_parser_name(self, parser_name, black_list):
        return (parser_name not in self._parsers_name) and (parser_name not in black_list)

    def _create_name_from_words(self, words, words_in_name, black_list):
        if len(words) <= words_in_name:
            proposed_name = '_'.join(words)
        else:
            proposed_name = '_'.join(words[i] for i in range(words_in_name))
        if self.is_free_parser_name(proposed_name, black_list):
            return proposed_name
        return self._find_free_by_number_appending(proposed_name, black_list)

    def propose_parser_name(self, line, regex_str, black_list):
        building_words = ParserNameManager._get_building_words(line, regex_str) or ['parser_name']
        return self._create_name_from_words(building_words, WORDS_IN_NAME, black_list)

    @classmethod
    def _get_building_words(cls, line, pattern_str):
        pattern = re.compile(pattern_str)
        matcher = pattern.match(line)
        if matcher is not None:
            groups = matcher.groups()
            for i in range(len(groups)):
                line = line.replace(groups[i], ' ')
        return [re.sub('[^0-9a-zA-Z]+', ' ', word.lower()) for word in line.split()]

    def _find_free_by_number_appending(self, word, black_list):
        for i in range(len(black_list) + 1):
            propsed_name = word + str(i + 1)
            if self.is_free_parser_name(propsed_name, black_list):
                return propsed_name
