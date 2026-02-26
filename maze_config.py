from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional


class MazeConfig(BaseModel):
    width: int = Field(ge=2)
    height: int = Field(ge=2)

    entry: tuple[int, int] = Field(...)
    exit: tuple[int, int] = Field(...)

    perfect: bool = Field(...)

    output_file: str = Field(pattern=r"^[a-zA-Z_]+\.txt$")

    seed: Optional[str] = Field(default=None)
    algorithm: str = "PRIM"

    pattern_width: int = Field(default=0)
    pattern_height: int = Field(default=0)
    pattern_abs_coords: list[tuple[int, int]] = Field(default_factory=list)

    # parse coords of entry and exit keys before
    @field_validator("entry", "exit", mode="before")
    @classmethod
    def parse_coords(cls, coords: str) -> tuple[int, int]:
        coords_splitted = coords.split(",")
        if len(coords_splitted) != 2:
            raise ValueError(
                "Coordinates in ENTRY and EXIT must be in format"
                f" 'ENTRY=1,2'. received: {coords}"
            )
        x, y = map(int, coords_splitted)
        return (x, y)

    # setup pattern dimensions
    @model_validator(mode="after")
    def create_pattern(self) -> "MazeConfig":
        pattern_design: list[str] = [
            "#...###",
            "#.....#",
            "###.###",
            "..#.#..",
            "..#.###",
        ]
        # setup width and height of pattern
        self.pattern_width = max(len(row) for row in pattern_design) + 2
        self.pattern_height = len(pattern_design) + 2

        pattern_coords: list[tuple[int, int]] = []
        self.pattern_abs_coords: list[tuple[int, int]] = []

        # if pattern doesnt fit, we dont fill pattern_coords and return
        if not self.can_fit_42():
            print(
                f"Maze {self.width}x{self.height} is too small for pattern "
                f"({self.pattern_width}x{self.pattern_height})"
            )
            return self

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
            self.pattern_abs_coords.append(
                (absolute_row, absolute_col),
            )
        return self

    # validate the config
    @model_validator(mode="after")
    def validate_config(self) -> "MazeConfig":

        # verify that entry and exit are in the limits of the maze
        for name, coord in [("ENTRY", self.entry), ("EXIT", self.exit)]:
            if not self._is_coords_in_limits(coord):
                raise ValueError(
                    f"{name} {coord} is out of maze bounds"
                    f" (0-{self.width - 1}, 0-{self.height - 1})"
                )

        # verifier que entry et exit sont pas les memes points
        if self.entry == self.exit:
            raise ValueError("ENTRY and EXIT positions must be different.")

        # verify that the pattern can fit in the maze and
        # if entry and exit are out of pattern
        if self.can_fit_42():
            if self.entry in self.pattern_abs_coords:
                raise ValueError(
                    f"ENTRY {self.entry} is inside the '42' pattern area."
                )
            if self.exit in self.pattern_abs_coords:
                raise ValueError(
                    f"EXIT {self.exit} is inside the '42' pattern area."
                )
        else:
            print(
                f"Error: Maze size {self.width}x{self.height} is too "
                "small for '42' pattern."
            )

        return self

    def _is_coords_in_limits(self, coord: tuple[int, int]) -> bool:
        x, y = coord
        if not (0 <= x < self.width) or not (0 <= y < self.height):
            return False
        return True

    def can_fit_42(self) -> bool:
        if (
            self.width >= self.pattern_width
            and self.height >= self.pattern_height
        ):
            return True
        return False
