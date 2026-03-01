import sys

from maze_config_parser import MazeConfigParser
from maze_config import MazeConfig
from mazegen.maze_generate import MazeGenerator
from maze_config_parser_error import MazeConfigParserError
from maze_display import display_maze
from pydantic import ValidationError


def display_hexa(maze: MazeGenerator) -> None:
    for y in range(maze.height):
        line: str = ""
        for x in range(maze.width):
            line += f"{maze.maze_grid[y][x]:X}"
        print(line)


def main() -> None:
    if len(sys.argv) != 2:
        sys.stderr.write("Error: Invalid arguments.\n")
        sys.stdout.write("Usage: python3 a_maze_ing.py <config_file.txt>\n")
        sys.exit(1)

    config_file: str = sys.argv[1]
    try:
        print(f"Attempting to load configuration from: {config_file}")
        config: MazeConfig = MazeConfigParser.load_config(config_file)
        maze: MazeGenerator = MazeGenerator(
            config.width,
            config.height,
            config.entry,
            config.exit,
            config.output_file,
            config.perfect,
            config.seed,
            config.algorithm,
        )
        display_hexa(maze)
        display_maze(maze)

    except MazeConfigParserError as err:
        sys.stderr.write(f"{err.__class__.__name__, err}")
    except ValidationError as err:
        for error in err.errors():
            field_path = " -> ".join(map(str, error["loc"])).upper()
            field = field_path if field_path else "validate_config"
            msg: str = error.get("msg", "empty")
            sys.stderr.write(f"MazeConfig error, Field {field} : {msg}")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Error: -> {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
    sys.exit(0)
