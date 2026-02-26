import random
from src.parser.maze_config import MazeConfig


class MazeGenerator:
    def __init__(self, config_data: MazeConfig):
        self.config_data: MazeConfig = config_data
        self.width: int = config_data.width
        self.height: int = config_data.height
        self.entry: tuple[int, int] = config_data.entry
        self.exit: tuple[int, int] = config_data.exit

        self.maze_grid: list[list[int]] = self.initialize_maze()
        self.visited_grid = self.generate_visited_grid()

    def generate_visited_grid(self) -> list[list[bool]]:
        visited_grid: list[list[bool]] = []
        visited_grid = [[False] * self.width for _ in range(self.height)]
        for pattern_y, pattern_x in self.config_data.pattern_centered_coords:
            visited_grid[pattern_y][pattern_x] = True
            self.maze_grid[pattern_y][pattern_x] = 15
        return visited_grid

    def initialize_maze(self) -> list[list[int]]:
        return [[15] * self.width for _ in range(self.height)]

    def generate_maze(self) -> None:
        stack: list[tuple] = []

        entry_y, entry_x = self.config_data.entry
        self.visited_grid[entry_y][entry_x] = True
        stack.append((entry_y, entry_x))

        while stack:
            current_y, current_x = stack[-1]
            valid_neighbors: list = []

            # North : y - 1
            if (
                current_y - 1 >= 0
                and self.visited_grid[current_y - 1][current_x] is False
            ):
                valid_neighbors.append(("North", current_y - 1, current_x))
            # South : y + 1
            if (
                current_y + 1 < self.height
                and self.visited_grid[current_y + 1][current_x] is False
            ):
                valid_neighbors.append(("South", current_y + 1, current_x))
            # East : x + 1
            if (
                current_x + 1 < self.width
                and self.visited_grid[current_y][current_x + 1] is False
            ):
                valid_neighbors.append(("East", current_y, current_x + 1))
            # West : x - 1
            if (
                current_x - 1 >= 0
                and self.visited_grid[current_y][current_x - 1] is False
            ):
                valid_neighbors.append(("West", current_y, current_x - 1))

            if valid_neighbors:
                chosen_direction, next_y, next_x = random.choice(
                    valid_neighbors
                )

                self.visited_grid[next_y][next_x] = True
                stack.append((next_y, next_x))
                if chosen_direction == "North":
                    self.maze_grid[current_y][current_x] -= 1
                    self.maze_grid[next_y][next_x] -= 4
                elif chosen_direction == "South":
                    self.maze_grid[current_y][current_x] -= 4
                    self.maze_grid[next_y][next_x] -= 1
                elif chosen_direction == "East":
                    self.maze_grid[current_y][current_x] -= 2
                    self.maze_grid[next_y][next_x] -= 8
                else:
                    self.maze_grid[current_y][current_x] -= 8
                    self.maze_grid[next_y][next_x] -= 2
            else:
                stack.pop()
