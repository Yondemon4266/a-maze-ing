import random
from typing import Optional


class MazeGenerator:
    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        output_file: str,
        perfect: bool,
        seed: Optional[str] = None,
        algorithm: Optional[str] = None,
    ):
        self.width: int = width
        self.height: int = height
        self.entry: tuple[int, int] = entry
        self.exit: tuple[int, int] = exit
        self.output_file: str = output_file
        self.perfect: bool = perfect
        self.seed: Optional[str] = seed
        self.algorithm: Optional[str] = algorithm
        self.pattern_centered_coords: list[tuple[int, int]] = []
        self.pattern_width: int = 0
        self.pattern_height: int = 0
        self.create_pattern()
        self.check_if_entry_or_exit_in_pattern()
        self._rng: random.Random = random.Random(seed)
        self.maze_grid: list[list[int]] = self.initialize_maze()
        self.visited_grid = self.generate_visited_grid()
        self.generate_maze()

    def generate_visited_grid(self) -> list[list[bool]]:
        visited_grid: list[list[bool]] = []
        visited_grid = [[False] * self.width for _ in range(self.height)]
        for pattern_y, pattern_x in self.pattern_centered_coords:
            visited_grid[pattern_y][pattern_x] = True
        return visited_grid

    def initialize_maze(self) -> list[list[int]]:
        return [[15] * self.width for _ in range(self.height)]

    def generate_maze(self) -> None:
        stack: list[tuple] = []

        entry_y, entry_x = self.entry
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

    def create_pattern(self) -> None:
        pattern_design: list[str] = [
            "#...###",
            "#.....#",
            "###.###",
            "..#.#..",
            "..#.###",
        ]
        # setup width and height of pattern
        self.pattern_width = max(len(row) for row in pattern_design)
        self.pattern_height = len(pattern_design)

        pattern_coords: list[tuple[int, int]] = []

        # if pattern doesnt fit, we dont fill pattern_coords and return
        if not self.can_fit_42():
            print(
                f"Error: Maze {self.width}x{self.height} is too small "
                f"for pattern ({self.pattern_width + 2}x"
                f"{self.pattern_height + 2})"
            )
        # we fill pattern_coords with the pattern design
        # and fill the abs pattern coords
        for row_idx, row_string in enumerate(pattern_design):
            for col_idx, char in enumerate(row_string):
                if char == "#":
                    pattern_coords.append((row_idx, col_idx))
        start_pattern_col: int = (self.width - self.pattern_width) // 2
        start_pattern_row: int = (self.height - self.pattern_height) // 2
        for row, col in pattern_coords:
            absolute_row: int = start_pattern_row + row
            absolute_col: int = start_pattern_col + col
            self.pattern_centered_coords.append(
                (absolute_row, absolute_col),
            )

    def check_if_entry_or_exit_in_pattern(self) -> None:
        if self.can_fit_42():
            if self.entry in self.pattern_centered_coords:
                raise ValueError(
                    f"ENTRY {self.entry} is inside the '42' pattern area."
                )
            if self.exit in self.pattern_centered_coords:
                raise ValueError(
                    f"EXIT {self.exit} is inside the '42' pattern area."
                )

    def can_fit_42(self) -> bool:
        if (
            self.width >= self.pattern_width + 2
            and self.height >= self.pattern_height + 2
        ):
            return True
        return False
