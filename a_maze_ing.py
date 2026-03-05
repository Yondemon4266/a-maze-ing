"""Entry-point script for the A-Maze-ing maze generator.

Usage::

    python3 a_maze_ing.py <config_file.txt>

Reads a configuration file, generates a maze, solves it, writes the
output, and launches an interactive MLX graphical display.
"""

import sys

from mazegen import MazeGenerator, MazeConfigParserError
from maze_display import display_maze
from pydantic import ValidationError


def get_maze_hexa(maze: MazeGenerator) -> list[str]:
    """Convert the maze grid to hexadecimal string lines.

    Each cell's wall bitmask (0–15) is encoded as a single
    hexadecimal character, and all cells in a row are concatenated
    into one string.

    Args:
        maze: A ``MazeGenerator`` instance with a populated grid.

    Returns:
        A list of strings, one per row, where each character is
        the hex representation of that cell's wall value.
    """
    lines: list[str] = []
    for y in range(maze.config.height):
        line: str = ""
        for x in range(maze.config.width):
            line += f"{maze.maze_grid[y][x]:X}"
        lines.append(line)
    return lines


def write_output_file(maze: MazeGenerator) -> None:
    """Write the maze data to the configured output file.

    The output file contains:
        1. Hexadecimal-encoded maze rows.
        2. A blank separator line.
        3. Entry coordinates as ``x,y``.
        4. Exit coordinates as ``x,y``.
        5. The solved path string.

    Args:
        maze: A ``MazeGenerator`` instance with a solved maze.
    """
    try:
        with open(maze.config.output_file, "w") as file:
            lines_hexa: list[str] = get_maze_hexa(maze)
            for line in lines_hexa:
                file.write(line + "\n")
            file.write("\n")
            entry_y, entry_x = maze.config.entry
            exit_y, exit_x = maze.config.exit
            file.write(",".join([str(entry_x), str(entry_y)]) + "\n")
            file.write(",".join([str(exit_x), str(exit_y)]) + "\n")
            file.write(str(maze.solved_path) + "\n")
    except OSError as err:
        print(err)


def main() -> None:
    """Parse CLI arguments, generate, solve, export, and display the maze.

    Expects exactly one command-line argument — the path to a
    configuration file.  Errors are reported to stderr and cause a
    non-zero exit code.
    """
    if len(sys.argv) != 2:
        sys.stderr.write("Error: Invalid arguments.\n")
        sys.stdout.write("Usage: python3 a_maze_ing.py <config_file.txt>\n")
        sys.exit(1)

    config_file_name: str = sys.argv[1]
    try:
        maze: MazeGenerator = MazeGenerator(config_file_name)
        maze.solve()
        write_output_file(maze)
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
