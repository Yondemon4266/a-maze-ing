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
        return (y, x)

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

        # verify that entry et exit are different points
        if self.entry == self.exit:
            raise ValueError("ENTRY and EXIT positions must be different.")

        # verify that the pattern can fit in the maze and
        # if entry and exit are out of pattern

        return self

    def _is_coords_in_limits(self, coord: tuple[int, int]) -> bool:
        y, x = coord
        if not (0 <= x < self.width) or not (0 <= y < self.height):
            return False
        return True
