"""Custom exception hierarchy for maze configuration parsing errors."""


class MazeConfigParserError(Exception):
    """Base exception for all maze configuration parser errors."""

    pass


class MazeConfigParserValueError(ValueError):
    """Raised when a configuration value is malformed or invalid."""

    pass


class MazeConfigParserFileError(MazeConfigParserError, OSError):
    """Raised when the configuration file cannot be opened or read."""

    pass
