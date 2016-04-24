import os.path


class LogType(object):
    def __init__(self, name, filename_matchers):
        self.name = name
        self._filename_matchers = filename_matchers

    # It will be generator
    def files_to_parse(self):
        # TODO: remove mock
        return [
            (
                'localhost', os.path.join(
                    *[
                        'whylog', 'tests', 'tests_log_reader', 'test_files', '003_match_time_range',
                        'node_1.log'
                    ]
                )
            )
        ]  # yapf: disable
