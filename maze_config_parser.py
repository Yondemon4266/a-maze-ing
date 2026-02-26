from maze_config import MazeConfig
from pydantic import ValidationError
from maze_parser_config_error import MazeConfigParserError
from maze_parser_config_error import MazeConfigParserFileError
from maze_parser_config_error import MazeConfigParserValueError


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
    except MazeConfigParserError as err:
        print(err.__class__.__name__, err)
    except ValidationError as err:
        for error in err.errors():
            field_path = " -> ".join(map(str, error["loc"])).upper()
            field = field_path if field_path else "validate_config"

            msg: str = error.get("msg", "empty")
            print(f"MazeConfig error, Field {field} : {msg}")
