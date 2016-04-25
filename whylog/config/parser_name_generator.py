import re

import six

NON_ALPHA_NUMERIC_REGEX = re.compile('[^0-9a-zA-Z]+')


class ParserNameGenerator(object):
    WORDS_COUNT_IN_NAME = 4

    def __init__(self, parsers):
        self._parsers = parsers

    def is_free_parser_name(self, parser_name, black_list):
        return (parser_name not in self._parsers) and (parser_name not in black_list)

    def _create_name_from_words(self, words, black_list):
        proposed_name = '_'.join(words[:self.WORDS_COUNT_IN_NAME])
        if self.is_free_parser_name(proposed_name, black_list):
            return proposed_name
        return self._find_free_by_number_appending(proposed_name, black_list)

    def propose_parser_name(self, line, regex_str, black_list):
        building_words = self._get_building_words(line, regex_str) or ['parser_name']
        return self._create_name_from_words(building_words, black_list)

    @classmethod
    def _get_building_words(cls, line, pattern_str):
        pattern = re.compile(pattern_str)
        matcher = pattern.match(line)
        if matcher is not None:
            groups = matcher.groups()
            for i in six.moves.range(len(groups)):
                line = line.replace(groups[i], ' ')
        return [re.sub(NON_ALPHA_NUMERIC_REGEX, ' ', word.lower()) for word in line.split()]

    def _find_free_by_number_appending(self, proposed_name, black_list):
        for i in six.moves.range(len(black_list) + 1):
            propsed_name = proposed_name + str(i + 1)
            if self.is_free_parser_name(propsed_name, black_list):
                return propsed_name
