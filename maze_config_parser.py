from maze_config import MazeConfig
from pydantic import ValidationError


class MazeConfigParserError(Exception):
    pass


class MazeConfigParserValueError(ValueError):
    pass


class MazeConfigParserFileError(OSError):
    pass


class MazeConfigParser:
    @staticmethod
    def read_config_file(filename: str) -> dict[str, str]:
        try:
            raw_config: dict[str, str] = {}
            with open(filename, "r") as file:
                for line in file:
                    line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        continue
                    splitted_line: list[str] = line.split("=")
                    if len(splitted_line) != 2:
                        raise MazeConfigParserValueError(
                            "Line must have only a key and a value "
                            f"(format:key=value) received: {splitted_line}"
                        )
                    key: str = splitted_line[0].strip()
                    value: str = splitted_line[1].strip()
                    raw_config[key.lower()] = value
            return raw_config
        except OSError as err:
            raise MazeConfigParserFileError(f"{err.filename}: {err.strerror}")

    @classmethod
    def load_config(cls, filename: str) -> MazeConfig:
        raw_config: dict[str, str] = cls.read_config_file(filename)
        return MazeConfig.model_validate(raw_config)


if __name__ == "__main__":
    try:
        maze_config: MazeConfig = MazeConfigParser.load_config("config.txt")
        print(maze_config)
        print(maze_config.__dict__)
    except ValidationError as err:
        print(err)
