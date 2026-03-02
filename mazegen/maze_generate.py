import random
from typing import Optional


class MazeGenerator:
    NORTH = 1  # 0001
    EAST = 2  # 0010
    SOUTH = 4  # 0100
    WEST = 8  # 1000

    OPPOSITE = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        output_file: str,
        perfect: bool,
        seed: Optional[str] = None,
        algorithm: str = "DFS",
    ):
        self.width: int = width
        self.height: int = height
        self.entry: tuple[int, int] = entry
        self.exit: tuple[int, int] = exit
        self.output_file: str = output_file
        self.perfect: bool = perfect
        self.seed: Optional[str] = seed
        self.algorithm: str = algorithm
        self.pattern_centered_coords: list[tuple[int, int]] = []
        self.pattern_width: int = 0
        self.pattern_height: int = 0
        self.create_pattern()
        self.check_if_entry_or_exit_in_pattern()
        self.maze_grid: list[list[int]] = self.initialize_maze()
        self.visited_grid = self.generate_visited_grid()
        self.accepted_algorithms: list[str] = ["dfs", "prim"]
        self.generate_maze()
        self.visited_solve = self.generate_visited_grid()
        self.solved_path: Optional[str] = None

    def generate_visited_grid(self) -> list[list[bool]]:
        visited_grid: list[list[bool]] = []
        visited_grid = [[False] * self.width for _ in range(self.height)]
        if self.can_fit_pattern():
            for pattern_row, pattern_col in self.pattern_centered_coords:
                visited_grid[pattern_row][pattern_col] = True

        return visited_grid

    def initialize_maze(self) -> list[list[int]]:
        return [[15] * self.width for _ in range(self.height)]

    def generate_maze(self) -> None:
        print(self.algorithm)
        self._rng: random.Random = random.Random(self.seed)
        if self.algorithm.lower() not in self.accepted_algorithms:
            raise ValueError(
                f"The selected algorithm {self.algorithm} "
                "is not implemented in our MazeGenerator"
            )
        if self.algorithm.lower() == "dfs":
            self.dfs_generate_algorithm()
        if self.algorithm.lower() == "prim":
            self.prim_generate_algorithm()

    def dfs_generate_algorithm(self) -> None:
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
                chosen_direction, next_row, next_col = self._rng.choice(
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

    def prim_generate_algorithm(self) -> None:
        entry_row, entry_col = self.entry
        self.visited_grid[entry_row][entry_col] = True

        valid_walls: list[tuple[int, int, int, int, int]] = (
            self._get_adj_walls(entry_col, entry_row)
        )
        while valid_walls:
            random_index = self._rng.randrange(len(valid_walls))
            col1, row1, col2, row2, direction_bit = valid_walls.pop(
                random_index
            )
            if not self.visited_grid[row2][col2]:
                self._break_wall(col1, row1, col2, row2, direction_bit)
                self.visited_grid[row2][col2] = True
                new_walls = self._get_adj_walls(col2, row2)
                valid_walls.extend(new_walls)

    def _get_adj_walls(
        self, col: int, row: int
    ) -> list[tuple[int, int, int, int, int]]:
        valid_walls: list[tuple[int, int, int, int, int]] = []
        directions = [
            (0, -1, self.NORTH),
            (1, 0, self.EAST),
            (0, 1, self.SOUTH),
            (-1, 0, self.WEST),
        ]

        for dcol, drow, direction_bit in directions:
            ncol, nrow = col + dcol, row + drow

            within_bounds: bool = (
                0 <= ncol < self.width and 0 <= nrow < self.height
            )
            if within_bounds and not self.visited_grid[nrow][ncol]:
                valid_walls.append((col, row, ncol, nrow, direction_bit))

        return valid_walls

    def _break_wall(
        self, x1: int, y1: int, x2: int, y2: int, direction: int
    ) -> None:
        self.maze_grid[y1][x1] &= ~direction
        self.maze_grid[y2][x2] &= ~self.OPPOSITE[direction]

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
        return (
            self.width >= self.pattern_width + 2
            and self.height >= self.pattern_height + 2
        )

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
                self.solved_path = current_path
                return current_path

            # 0 means no wall in that direction. 1=North, 2=East, 4=South,
            # 8=West.
            # AND cell above is unvisited

            if (
                self.maze_grid[current_row][current_col] & 1 == 0
                and self.visited_solve[current_row - 1][current_col] is False
            ):
                self.visited_solve[current_row - 1][current_col] = True
                path_solve.append(
                    (current_row - 1, current_col, current_path + "N")
                )

            if (
                self.maze_grid[current_row][current_col] & 4 == 0
                and self.visited_solve[current_row + 1][current_col] is False
            ):
                self.visited_solve[current_row + 1][current_col] = True
                path_solve.append(
                    (current_row + 1, current_col, current_path + "S")
                )

            if (
                self.maze_grid[current_row][current_col] & 2 == 0
                and self.visited_solve[current_row][current_col + 1] is False
            ):
                self.visited_solve[current_row][current_col + 1] = True
                path_solve.append(
                    (current_row, current_col + 1, current_path + "E")
                )

            if (
                self.maze_grid[current_row][current_col] & 8 == 0
                and self.visited_solve[current_row][current_col - 1] is False
            ):
                self.visited_solve[current_row][current_col - 1] = True
                path_solve.append(
                    (current_row, current_col - 1, current_path + "W")
                )

        return None

    def regenerate(self) -> None:
        self.maze_grid = self.initialize_maze()
        self.visited_grid = self.generate_visited_grid()
        self.visited_solve = self.generate_visited_grid()
        self.generate_maze()
