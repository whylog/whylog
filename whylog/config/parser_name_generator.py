import re

import six

NON_ALPHA_NUMERIC_REGEX = re.compile('[^0-9a-zA-Z]+')


class ParserNameGenerator(object):
    def __init__(self, parsers):
        self._parsers = parsers

    def is_free_parser_name(self, parser_name, black_list):
        return (parser_name not in self._parsers) and (parser_name not in black_list)

    def _create_name_from_words(self, words, black_list, words_count_in_name):
        proposed_name = '_'.join(words[:words_count_in_name])
        if self.is_free_parser_name(proposed_name, black_list):
            return proposed_name
        return self._find_free_by_number_appending(proposed_name, black_list)

    def propose_parser_name(self, line, regex_str, black_list, words_count_in_name):
        building_words = self._get_building_words(line, regex_str) or ['parser_name']
        return self._create_name_from_words(building_words, black_list, words_count_in_name)

    @classmethod
    def _get_building_words(cls, line, pattern_str):
        matcher = re.match(pattern_str, line)
        if matcher is not None:
            for group in matcher.groups():
                line = line.replace(group, ' ')
        return [re.sub(NON_ALPHA_NUMERIC_REGEX, ' ', word.lower()) for word in line.split()]

    def _find_free_by_number_appending(self, proposed_name, black_list):
        for i in six.moves.range(len(black_list) + 1):
            propsed_name = proposed_name + str(i + 1)
            if self.is_free_parser_name(propsed_name, black_list):
                return propsed_name
