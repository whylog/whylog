import os.path


class AFewLinesLogParams:
    FILE_NAME = "a_few_lines.log"
    SINGLE_LINE_LENGTH = 10
    NUMBER_OF_LINES = 10

    @classmethod
    def get_line_with_borders(cls, offset):
        """
        returns: line content, beginning offset, ending offset
        """
        assert 0 <= offset < cls.NUMBER_OF_LINES * cls.SINGLE_LINE_LENGTH
        return ('aaa-%d-bbb' % (offset // 10)), (offset // 10) * 10, (offset // 10) * 10 + 9


class TestPaths(object):
    path_test_files = ['whylog', 'tests', 'tests_log_reader', 'test_files']

    @classmethod
    def get_file_path(cls, filename):
        prefix_path = os.path.join(*TestPaths.path_test_files)
        return os.path.join(prefix_path, filename)
