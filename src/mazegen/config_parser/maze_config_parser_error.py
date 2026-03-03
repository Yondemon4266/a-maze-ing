class MazeConfigParserError(Exception):
    pass


class MazeConfigParserValueError(ValueError):
    pass


class MazeConfigParserFileError(MazeConfigParserError, OSError):
    pass
