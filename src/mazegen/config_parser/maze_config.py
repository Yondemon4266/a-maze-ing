"""Pydantic model defining the maze configuration schema and validation."""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional


class MazeConfig(BaseModel):
    """Configuration model for maze generation parameters.

    Validates and stores all settings parsed from a configuration file,
    including dimensions, entry/exit coordinates, algorithm choice, and
    output file path.

    Attributes:
        width: Maze width in cells (minimum 2).
        height: Maze height in cells (minimum 2).
        entry: Entry coordinates as (row, col).
        exit: Exit coordinates as (row, col).
        perfect: Whether the maze should be perfect (no loops).
        output_file: Output filename matching ``[a-zA-Z_]+.txt``.
        seed: Optional RNG seed for reproducible generation.
        algorithm: Generation algorithm name (default ``"DFS"``).
    """

    width: int = Field(ge=2, le=100)
    height: int = Field(ge=2, le=100)

    entry: tuple[int, int] = Field(...)
    exit: tuple[int, int] = Field(...)

    perfect: bool = Field(...)

    output_file: str = Field(pattern=r"^[a-zA-Z_]+\.txt$")

    seed: Optional[str] = Field(default=None)
    algorithm: str = Field(default="DFS")

    @field_validator("entry", "exit", mode="before")
    @classmethod
    def parse_coords(cls, coords: str) -> tuple[int, int]:
        """Parse coordinate strings into (row, col) tuples.

        Converts a comma-separated ``"x,y"`` string from the config file
        into an internal ``(row, col)`` tuple by swapping x and y.

        Args:
            coords: Coordinate string in ``"x,y"`` format.

        Returns:
            A ``(row, col)`` tuple of integers.

        Raises:
            ValueError: If the string does not contain exactly two
                comma-separated values.
        """
        coords_splitted = coords.split(",")
        if len(coords_splitted) != 2:
            raise ValueError(
                "Coordinates in ENTRY and EXIT must be in format"
                f" 'ENTRY=1,2'. received: {coords}"
            )
        x, y = map(int, coords_splitted)
        return (y, x)

    @model_validator(mode="after")
    def validate_config(self) -> "MazeConfig":
        """Validate cross-field constraints after individual field parsing.

        Ensures that entry and exit coordinates are within maze bounds
        and that they refer to different cells.

        Returns:
            The validated ``MazeConfig`` instance.

        Raises:
            ValueError: If entry/exit are out of bounds or identical.
        """

        # verify that entry and exit are in the limits of the maze
        for name, coord in [("ENTRY", self.entry), ("EXIT", self.exit)]:
            if not self._is_coords_in_limits(coord):
                raise ValueError(
                    f"{name} {coord} is out of maze bounds"
                    f" (0-{self.width - 1}, 0-{self.height - 1})"
                )

        # verify that entry et exit are different points
        if self.entry == self.exit:
            raise ValueError("ENTRY and EXIT positions must be different.")

        # verify that the pattern can fit in the maze and
        # if entry and exit are out of pattern

        return self

    def _is_coords_in_limits(self, coord: tuple[int, int]) -> bool:
        """Check whether a coordinate pair falls within the maze boundaries.

        Args:
            coord: A ``(row, col)`` tuple to validate.

        Returns:
            ``True`` if the coordinate is inside the maze, ``False`` otherwise.
        """
        y, x = coord
        if not (0 <= x < self.width) or not (0 <= y < self.height):
            return False
        return True
