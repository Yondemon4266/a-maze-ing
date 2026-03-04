import random
from typing import Optional
from .config_parser.maze_config import MazeConfig
from .config_parser.maze_config_parser import MazeConfigParser


class MazeGenerator:
    NORTH = 1  # 0001
    EAST = 2  # 0010
    SOUTH = 4  # 0100
    WEST = 8  # 1000

    OPPOSITE = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}

    def __init__(self, config_file_name: str):
        self.config: MazeConfig = MazeConfigParser.load_config(
            config_file_name
        )
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
        visited_grid = [
            [False] * self.config.width for _ in range(self.config.height)
        ]
        if self.can_fit_pattern():
            for pattern_row, pattern_col in self.pattern_centered_coords:
                visited_grid[pattern_row][pattern_col] = True

        return visited_grid

    def initialize_maze(self) -> list[list[int]]:
        return [[15] * self.config.width for _ in range(self.config.height)]

    def generate_maze(self) -> None:
        self._rng: random.Random = random.Random(self.config.seed)
        if self.config.algorithm.lower() not in self.accepted_algorithms:
            raise ValueError(
                f"The selected algorithm {self.config.algorithm} "
                "is not implemented in our MazeGenerator"
            )
        if self.config.algorithm.lower() == "dfs":
            self.dfs_generate_algorithm()
        if self.config.algorithm.lower() == "prim":
            self.prim_generate_algorithm()

        if not self.config.perfect:
            self.make_imperfect()

    def dfs_generate_algorithm(self) -> None:
        stack: list[tuple[int, int]] = []
        entry_row, entry_col = self.config.entry

        self.visited_grid[entry_row][entry_col] = True
        stack.append((entry_row, entry_col))

        # DFS Backtracking loop: explore random unvisited neighbors,
        # or backtrack when hitting a dead end

        while stack:
            current_row, current_col = stack[-1]
            valid_neighbors: list[tuple[int, int, int, int, int]] = []

            valid_neighbors.extend(
                self._get_adj_walls(current_row, current_col)
            )

            if valid_neighbors:
                (
                    current_row,
                    current_col,
                    next_row,
                    next_col,
                    chosen_direction,
                ) = self._rng.choice(valid_neighbors)

                self.visited_grid[next_row][next_col] = True
                stack.append((next_row, next_col))
                self._break_wall(
                    current_row,
                    current_col,
                    next_row,
                    next_col,
                    chosen_direction,
                )
            else:
                stack.pop()

    def prim_generate_algorithm(self) -> None:
        entry_row, entry_col = self.config.entry
        self.visited_grid[entry_row][entry_col] = True

        valid_cells: list[tuple[int, int, int, int, int]] = (
            self._get_adj_walls(entry_row, entry_col)
        )
        while valid_cells:
            random_index = self._rng.randrange(len(valid_cells))
            current_row, current_col, next_row, next_col, direction_bit = (
                valid_cells.pop(random_index)
            )
            if not self.visited_grid[next_row][next_col]:
                self._break_wall(
                    current_row, current_col, next_row, next_col, direction_bit
                )
                self.visited_grid[next_row][next_col] = True
                new_cells = self._get_adj_walls(next_row, next_col)
                valid_cells.extend(new_cells)

    def _get_adj_walls(
        self, current_row: int, current_col: int
    ) -> list[tuple[int, int, int, int, int]]:
        valid_cells: list[tuple[int, int, int, int, int]] = []
        directions = [
            (-1, 0, self.NORTH),
            (0, 1, self.EAST),
            (1, 0, self.SOUTH),
            (0, -1, self.WEST),
        ]

        for drow, dcol, direction_bit in directions:
            next_row, next_col = current_row + drow, current_col + dcol

            within_bounds: bool = (
                0 <= next_col < self.config.width
                and 0 <= next_row < self.config.height
            )
            if within_bounds and not self.visited_grid[next_row][next_col]:
                valid_cells.append(
                    (
                        current_row,
                        current_col,
                        next_row,
                        next_col,
                        direction_bit,
                    )
                )

        return valid_cells

    def _break_wall(
        self,
        current_row: int,
        current_col: int,
        next_row: int,
        next_col: int,
        direction: int,
    ) -> None:
        self.maze_grid[current_row][current_col] -= direction
        self.maze_grid[next_row][next_col] -= self.OPPOSITE[direction]

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
                f"Error: Maze {self.config.width}x{self.config.height} is "
                f"too small for pattern ({self.pattern_width + 2}x"
                f"{self.pattern_height + 2})"
            )
        else:
            start_pattern_col: int = (
                self.config.width - self.pattern_width
            ) // 2
            start_pattern_row: int = (
                self.config.height - self.pattern_height
            ) // 2

            for row, col in pattern_coords:
                absolute_row: int = start_pattern_row + row
                absolute_col: int = start_pattern_col + col
                self.pattern_centered_coords.append(
                    (absolute_row, absolute_col),
                )

    def check_if_entry_or_exit_in_pattern(self) -> None:
        if self.can_fit_pattern():
            if self.config.entry in self.pattern_centered_coords:
                raise ValueError(
                    f"ENTRY {self.config.entry} is inside the '42' "
                    "pattern area."
                )
            if self.config.exit in self.pattern_centered_coords:
                raise ValueError(
                    f"EXIT {self.config.exit} is inside the '42' pattern area."
                )

    def can_fit_pattern(self) -> bool:
        return (
            self.config.width >= self.pattern_width + 2
            and self.config.height >= self.pattern_height + 2
        )

    def solve(self) -> str | None:
        self.visited_solve = self.generate_visited_grid()

        path_solve: list[tuple[int, int, str]] = []
        entry_row, entry_col = self.config.entry

        path_solve.append((entry_row, entry_col, ""))
        self.visited_solve[entry_row][entry_col] = True

        # BFS loop: continue as long as there are cells left to explore
        while path_solve:
            current_row, current_col, current_path = path_solve.pop(0)
            if (current_row, current_col) == self.config.exit:
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
                self.maze_grid[current_row][current_col] & self.WEST == 0
                and self.visited_solve[current_row][current_col - 1] is False
            ):
                self.visited_solve[current_row][current_col - 1] = True
                path_solve.append(
                    (current_row, current_col - 1, current_path + "W")
                )

        return None

    def make_imperfect(self) -> None:
        chance: float = 0.90
        for current_row in range(self.config.height - 1):
            for current_col in range(self.config.width - 1):
                if (current_row, current_col) in self.pattern_centered_coords:
                    continue

                for drow, dcol, direction in [
                    (0, 1, self.EAST),
                    (1, 0, self.SOUTH),
                ]:
                    next_row, next_col = current_row + drow, current_col + dcol
                    if (
                        0 <= next_row < self.config.height
                        and 0 <= next_col < self.config.width
                        and (next_row, next_col)
                        not in self.pattern_centered_coords
                    ):

                        if (
                            self.maze_grid[current_row][current_col]
                            & direction
                        ):
                            if self._rng.random() < chance:
                                if (
                                    bin(
                                        self.maze_grid[current_row][
                                            current_col
                                        ]
                                    ).count("1")
                                    > 1
                                    and bin(
                                        self.maze_grid[next_row][next_col]
                                    ).count("1")
                                    > 1
                                ):
                                    self._break_wall(
                                        current_row,
                                        current_col,
                                        next_row,
                                        next_col,
                                        direction,
                                    )

    def regenerate(self) -> None:
        self.maze_grid = self.initialize_maze()
        self.visited_grid = self.generate_visited_grid()
        self.visited_solve = self.generate_visited_grid()
        self.generate_maze()
