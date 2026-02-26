import sys
import random


def generate_maze(config_data: dict,
                  maze_grid: list[int],
                  visited_grid: list[bool]
                  ) -> None:

    stack: list[tuple] = []
    parse_height: int = config_data.get("HEIGHT")
    parse_width: int = config_data.get("WIDTH")

    X, Y = config_data.get("ENTRY")
    visited_grid[X][Y] = True
    stack.append((X, Y))

    while stack:
        current_x, current_y = stack[-1]
        valid_neighbors: list = []
        if (current_x - 1 >= 0 and
                visited_grid[current_x - 1][current_y] is False):
            valid_neighbors.append(("North", current_x - 1, current_y))
        if (current_x + 1 < parse_height and
                visited_grid[current_x + 1][current_y] is False):
            valid_neighbors.append(("South", current_x + 1, current_y))
        if (current_y + 1 < parse_width and
                visited_grid[current_x][current_y + 1] is False):
            valid_neighbors.append(("East", current_x, current_y + 1))
        if (current_y - 1 >= 0 and
                visited_grid[current_x][current_y - 1] is False):
            valid_neighbors.append(("West", current_x, current_y - 1))

        if valid_neighbors:
            chosen_direction, next_x, next_y = random.choice(valid_neighbors)
            visited_grid[next_x][next_y] = True
            stack.append((next_x, next_y))
            if chosen_direction == "North":
                maze_grid[current_x][current_y] -= 1
                maze_grid[next_x][next_y] -= 4
            elif chosen_direction == "South":
                maze_grid[current_x][current_y] -= 4
                maze_grid[next_x][next_y] -= 1
            elif chosen_direction == "East":
                maze_grid[current_x][current_y] -= 2
                maze_grid[next_x][next_y] -= 8
            else:
                maze_grid[current_x][current_y] -= 8
                maze_grid[next_x][next_y] -= 2
        else:
            stack.pop()


def create_pattern(config_data: dict, visited_grid: list[bool]) -> None:

    parse_height: int = config_data.get("HEIGHT")
    parse_width: int = config_data.get("WIDTH")
    pattern_tuples: list[tuple] = []

    pattern_design: list[str] = [
        "#...###",
        "#.....#",
        "###.###",
        "..#.#..",
        "..#.###"
    ]

    for row_idx, row_string in enumerate(pattern_design):
        for col_idx, char in enumerate(row_string):
            if char == "#":
                pattern_tuples.append([row_idx, col_idx])

    pattern_width: int = max(len(row) for row in pattern_design)
    pattern_height: int = len(pattern_design)

    if parse_width < pattern_width or parse_height < pattern_height:
        sys.stderr.write("Maze is to small to display pattern\n")
    else:
        start_pattern_col = (parse_width - pattern_width) // 2
        start_pattern_row = (parse_height - pattern_height) // 2
        for row, col in pattern_tuples:
            real_row_pattern = start_pattern_row + row
            real_col_pattern = start_pattern_col + col
            visited_grid[real_row_pattern][real_col_pattern] = True


def generate_visited_grid(config_data: dict) -> list[bool]:

    parse_width: int = config_data.get("WIDTH")
    parse_height: int = config_data.get("HEIGHT")
    visited_grid: list[bool] = []
    for _ in range(0, parse_height):
        current_row = []
        for _ in range(0, parse_width):
            current_row.append(False)
        visited_grid.append(current_row)

    return visited_grid


def initialize_maze(config_data: dict) -> list[int]:
    parse_width: int = config_data.get("WIDTH")
    parse_height: int = config_data.get("HEIGHT")
    init_grid: list[int] = []

    for _ in range(0, parse_height):
        current_row = []
        for _ in range(0, parse_width):
            current_row.append(15)
        init_grid.append(current_row)

    return init_grid


if __name__ == "__main__":
    config_data = {
        "WIDTH": 10,
        "HEIGHT": 10,
        "ENTRY": (1, 1)
    }
    maze_grid: list[int] = initialize_maze(config_data)
    visited_grid: list[bool] = generate_visited_grid(config_data)
    pattern: dict[str, int] = create_pattern(config_data, visited_grid)
    generate_maze(config_data, maze_grid, visited_grid)
    print(f"{maze_grid}")
