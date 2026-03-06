"""mazegen — maze generation and configuration parsing package.

Exposes the main ``MazeGenerator`` class and the base configuration
parsing exception ``MazeConfigParserError`` for convenient top-level
imports.
"""

from mazegen.maze_generate import MazeGenerator
from mazegen.config_parser.maze_config_parser_error import (
    MazeConfigParserError,
)

__all__ = ["MazeGenerator", "MazeConfigParserError"]
