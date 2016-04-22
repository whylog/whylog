import re


class ParserNameManager(object):
    def __init__(self, parsers):
        self._parsers_name = set()
        for parser_name in parsers:
            self._parsers_name.add(parser_name)

    def add_new_parser_name(self, parser_name):
        self._parsers_name.add(parser_name)

    def is_free_parser_name(self, parser_name, black_list):
        return (parser_name not in self._parsers_name) and (parser_name not in black_list)

    def _try_get_simple_name_else_append_number(self, word, black_list):
        if self.is_free_parser_name(word, black_list):
            return word
        return self._find_free_by_number_appending(word, black_list)

    def propose_parser_name(self, line, regex_str, black_list):
        building_words = ParserNameManager._get_building_words(line, regex_str)
        if not building_words:
            return self._find_free_by_number_appending('parser_name', black_list)
        if len(building_words) == 1:
            self._try_get_simple_name_else_append_number(building_words[0], black_list)
        proposed_name = building_words[0] + '_' + building_words[1]
        return self._try_get_simple_name_else_append_number(proposed_name, black_list)

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
