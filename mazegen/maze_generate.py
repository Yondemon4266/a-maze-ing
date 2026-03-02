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

        self._rng: random.Random = random.Random(seed)

        self.create_pattern()
        self.maze_grid: list[list[int]] = self.initialize_maze()
        self.visited_grid = self.generate_visited_grid()
        self.generate_maze()
        self.visited_solve = self.generate_visited_grid()

    def generate_visited_grid(self) -> list[list[bool]]:
        visited_grid: list[list[bool]] = []
        visited_grid = [[False] * self.width for _ in range(self.height)]
        if self.can_fit_pattern():
            for pattern_row, pattern_col in self.pattern_centered_coords:
                visited_grid[pattern_row][pattern_col] = True

        # create maze sides
        else:
            for col in range(self.width):
                visited_grid[0][col] = True
                visited_grid[self.height - 1][col] = True
            for row in range(self.height):
                visited_grid[row][0] = True
                visited_grid[row][self.width - 1] = True

        return visited_grid

    def initialize_maze(self) -> list[list[int]]:
        return [[15] * self.width for _ in range(self.height)]

    def generate_maze(self) -> None:
        stack: list[tuple[int, int]] = []
        entry_row, entry_col = self.entry

        self.visited_grid[entry_row][entry_col] = True
        stack.append((entry_row, entry_col))

        # DFS Backtracking loop: explore random unvisited neighbors,
        # or backtrack when hitting a dead end
        while stack:
            current_row, current_col = stack[-1]
            valid_neighbors: list = []

            # North : y - 1
            if (
                current_row - 1 >= 0
                and self.visited_grid[current_row - 1][current_col] is False
            ):
                valid_neighbors.append(("North", current_row - 1, current_col))
            # South : y + 1
            if (
                current_row + 1 < self.height
                and self.visited_grid[current_row + 1][current_col] is False
            ):
                valid_neighbors.append(("South", current_row + 1, current_col))
            # East : x + 1
            if (
                current_col + 1 < self.width
                and self.visited_grid[current_row][current_col + 1] is False
            ):
                valid_neighbors.append(("East", current_row, current_col + 1))
            # West : x - 1
            if (
                current_col - 1 >= 0
                and self.visited_grid[current_row][current_col - 1] is False
            ):
                valid_neighbors.append(("West", current_row, current_col - 1))

            if valid_neighbors:
                chosen_direction, next_row, next_col = random.choice(
                    valid_neighbors
                )

                self.visited_grid[next_row][next_col] = True
                stack.append((next_row, next_col))
                if chosen_direction == "North":
                    self.maze_grid[current_row][current_col] -= 1
                    self.maze_grid[next_row][next_col] -= 4
                elif chosen_direction == "South":
                    self.maze_grid[current_row][current_col] -= 4
                    self.maze_grid[next_row][next_col] -= 1
                elif chosen_direction == "East":
                    self.maze_grid[current_row][current_col] -= 2
                    self.maze_grid[next_row][next_col] -= 8
                elif chosen_direction == "West":
                    self.maze_grid[current_row][current_col] -= 8
                    self.maze_grid[next_row][next_col] -= 2
            else:
                stack.pop()

    def create_pattern(self) -> None:
        pattern_coords: list[tuple[int, int]] = []

        pattern_design: list[str] = [
            "#...###",
            "#.....#",
            "###.###",
            "..#.#..",
            "..#.###",
        ]

        # fill pattern_coords with the position of "#"
        for row_idx, row_string in enumerate(pattern_design):
            for col_idx, char in enumerate(row_string):
                if char == "#":
                    pattern_coords.append((row_idx, col_idx))

        self.pattern_width = max(len(row) for row in pattern_design)
        self.pattern_height = len(pattern_design)

        # if pattern doesnt fit, we dont fill pattern_coords
        if not self.can_fit_pattern():
            print(
                f"Error: Maze {self.width}x{self.height} is too small "
                f"for pattern ({self.pattern_width + 2}x"
                f"{self.pattern_height + 2})"
            )
        else:
            start_pattern_col: int = (self.width - self.pattern_width) // 2
            start_pattern_row: int = (self.height - self.pattern_height) // 2

            for row, col in pattern_coords:
                absolute_row: int = start_pattern_row + row
                absolute_col: int = start_pattern_col + col
                self.pattern_centered_coords.append(
                    (absolute_row, absolute_col),
                )

    def check_if_entry_or_exit_in_pattern(self) -> None:
        if self.can_fit_pattern():
            if self.entry in self.pattern_centered_coords:
                raise ValueError(
                    f"ENTRY {self.entry} is inside the '42' pattern area."
                )
            if self.exit in self.pattern_centered_coords:
                raise ValueError(
                    f"EXIT {self.exit} is inside the '42' pattern area."
                )

    def can_fit_pattern(self) -> bool:
        return (self.width >= self.pattern_width + 2 and
                self.height >= self.pattern_height + 2)

    def solve(self) -> str | None:
        self.visited_solve = self.generate_visited_grid()

        path_solve: list[tuple[int, int, str]] = []
        entry_row, entry_col = self.entry

        path_solve.append((entry_row, entry_col, ""))
        self.visited_solve[entry_row][entry_col] = True

        # BFS loop: continue as long as there are cells left to explore
        while path_solve:
            current_row, current_col, current_path = path_solve.pop(0)
            if (current_row, current_col) == self.exit:
                return current_path

        # 0 means no wall in that direction. 1=North, 2=East, 4=South, 8=West.
        # AND cell above is unvisited

            if (self.maze_grid[current_row][current_col] & 1 == 0 and
                    self.visited_solve[current_row - 1][current_col] is False):
                self.visited_solve[current_row - 1][current_col] = True
                path_solve.append((
                    current_row - 1, current_col, current_path + "N"))

            if (self.maze_grid[current_row][current_col] & 4 == 0 and
                    self.visited_solve[current_row + 1][current_col] is False):
                self.visited_solve[current_row + 1][current_col] = True
                path_solve.append((
                    current_row + 1, current_col, current_path + "S"))

            if (self.maze_grid[current_row][current_col] & 2 == 0 and
                    self.visited_solve[current_row][current_col + 1] is False):
                self.visited_solve[current_row][current_col + 1] = True
                path_solve.append((
                    current_row, current_col + 1, current_path + "E"))

            if (self.maze_grid[current_row][current_col] & 8 == 0 and
                    self.visited_solve[current_row][current_col - 1] is False):
                self.visited_solve[current_row][current_col - 1] = True
                path_solve.append((
                    current_row, current_col - 1, current_path + "W"))

        return None

    def regenerate(self) -> None:
        self.maze_grid = self.initialize_maze()
        self.visited_grid = self.generate_visited_grid()
        self.generate_maze()
        self.visited_solve = self.generate_visited_grid()
