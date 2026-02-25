import sys


def main() -> None:
    if len(sys.argv) != 2:
        sys.stderr.write("Error: Invalid arguments.\n")
        sys.stdout.write("Usage: python3 a_maze_ing.py <config_file.txt>\n")
        sys.exit(1)

    config_file: str = sys.argv[1]
    try:
        print(f"Attempting to load configuration from: {config_file}")
        config_data = parse_config(config_file)
        maze_grid = generate_maze(config_data)
        solution_path = solve_maze(maze_grid)
        render_maze(maze_grid, solution_path)

    except FileNotFoundError:
        sys.stderr.write("Error: The configuration file"
                         f"'{config_file}' was not found.\n")
        sys.exit(1)
    except PermissionError:
        sys.stderr.write("Error: Permission denied to read"
                         f"'{config_file}'.\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Error: -> {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
    sys.exit(0)