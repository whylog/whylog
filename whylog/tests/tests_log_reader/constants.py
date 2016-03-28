import os.path


class AFewLinesLogParams:
    FILE_NAME = "a_few_lines.log"
    SINGLE_LINE_LENGTH = 10


class TestPaths(object):
    path_test_files = ['whylog', 'tests', 'tests_log_reader', 'test_files']

    @classmethod
    def get_file_path(cls, filename):
        prefix_path = os.path.join(*TestPaths.path_test_files)
        return os.path.join(prefix_path, filename)
