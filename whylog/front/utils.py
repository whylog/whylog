class FrontInput(object):
    """
    Object of this class represents line in the file.
    """

    def __init__(self, offset, line_content, line_source):
        """
        Basic constructor of FrontInput.
        :param offset: byte of the first character of line in the file.
        :param line_content: the content of the line.
        :param line_source: object of LineSource.
        """
        self.offset = offset
        self.line_content = line_content
        self.line_source = line_source

    def __repr__(self):
        return "FrontInput(%s:%s: %s)" % (self.line_source, self.offset, self.line_content)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @classmethod
    def from_clue(cls, clue):
        return FrontInput(clue.line_offset, clue.line_prefix_content, clue.line_source)
