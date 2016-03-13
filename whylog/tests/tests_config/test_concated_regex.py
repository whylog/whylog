from unittest import TestCase

from whylog.config import RegexParserFactory
from whylog.config.parsers import ConcatedRegexParser
from whylog.teacher.user_intent import UserParserIntent

content1 = "2015-12-03 12:08:09 Connection error occurred on alfa36. Host name: 2"
content2 = "2015-12-03 12:10:10 Data migration from alfa36 to alfa21 failed. Host name: 2"
content3 = "2015-12-03 12:11:00 Data is missing at alfa21. Loss = 567.02 GB. Host name: 101"
content4 = "root cause"

regex1 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Connection error occurred on (.*)\. Host name: (.*)$"
regex2 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data migration from (.*) to (.*) failed\. Host name: (.*)$"
regex3 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)\. Loss = (.*) GB\. Host name: (.*)$"
regex4 = "^root cause$"
regex5 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing"
regex6 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*)$"

# convertions
to_date = "date"

parser_intent1 = UserParserIntent("connectionerror", "hydra", regex1, [1], {1: to_date})
parser_intent2 = UserParserIntent("datamigration", "hydra", regex2, [1], {1: to_date})
parser_intent3 = UserParserIntent("lostdata", "filesystem", regex3, [1], {1: to_date})
parser_intent4 = UserParserIntent("rootcause", "filesystem", regex4, [], {})
parser_intent5 = UserParserIntent("date", "filesystem", regex5, [1], {1: to_date})
parser_intent6 = UserParserIntent("onlymissdata", "filesystem", regex6, [1], {1: to_date})


class TestConcatedRegexParser(TestCase):
    def test_concated_regex(self):
        parser1 = RegexParserFactory.create_from_intent(parser_intent1)
        parser2 = RegexParserFactory.create_from_intent(parser_intent2)
        parser3 = RegexParserFactory.create_from_intent(parser_intent3)
        parser4 = RegexParserFactory.create_from_intent(parser_intent4)
        parser5 = RegexParserFactory.create_from_intent(parser_intent5)
        parser6 = RegexParserFactory.create_from_intent(parser_intent6)

        concated = ConcatedRegexParser([parser1, parser2, parser3, parser4, parser5, parser6])

        assert concated.get_extracted_regex_params("aaaaa") == {}
        assert concated.get_extracted_regex_params(content1) == {
            parser1.name: [
                "2015-12-03 12:08:09", "alfa36", "2"
            ]
        }
        assert concated.get_extracted_regex_params(content2) == {
            parser2.name: [
                "2015-12-03 12:10:10", "alfa36", "alfa21", "2"
            ]
        }
        assert concated.get_extracted_regex_params(content3) == {
            parser3.name: ["2015-12-03 12:11:00", "alfa21", "567.02", "101"],
            parser5.name: ["2015-12-03 12:11:00"],
            parser6.name: ["2015-12-03 12:11:00", "alfa21. Loss = 567.02 GB. Host name: 101"],
        }

        assert concated.get_extracted_regex_params(content4) == {parser4.name: []}