import re
import six
import uuid
from ordered_set import OrderedSet


class ParserNameManager(object):
    def __init__(self, parsers):
        self._parsers_name = OrderedSet()
        for parser in parsers:
            self._parsers_name.add(parser)

    def add_new_parser_name(self, parser_name):
        self._parsers_name.add(parser_name)

    def is_free_parser_name(self, parser_name):
        return parser_name not in self._parsers_name

    def propose_parser_name(self, line, regex_str, black_list):
        building_words = ParserNameManager._get_building_words(line, regex_str)
        if not building_words:
            return uuid.uuid4()
        if len(building_words) == 1:
            if self._is_unique_parser_name(building_words[0], black_list):
                return building_words[0]
            else:
                return self._find_free_by_number_appending(building_words[0], black_list)
        for i in range(len(building_words) - 1):
            propsed_name = building_words[i] + '_' + building_words[i + 1]
            if self._is_unique_parser_name(propsed_name, black_list):
                return propsed_name
        return self._find_free_by_number_appending(
            building_words[0] + '_' + building_words[1], black_list
        )

    def _is_unique_parser_name(self, parser_name, black_list):
        return self.is_free_parser_name(parser_name) and (parser_name not in black_list)

    @classmethod
    def _get_building_words(cls, line, regex_str):
        regex = re.compile(regex_str)
        matched = regex.match(line)
        if matched is not None:
            groups = matched.groups()
            for i in six.moves.range(len(groups)):
                line = line.replace(groups[i], '')
        line = re.sub('[,.;:]', '', line)
        return [word.lower() for word in line.split()]

    def _find_free_by_number_appending(self, word, black_list):
        for i in six.moves.range(len(black_list) + 1):
            propsed_name = word + str(i + 1)
            if self._is_unique_parser_name(propsed_name, black_list):
                return propsed_name
