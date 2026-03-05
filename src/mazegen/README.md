*This project has been created as part of the 42 curriculum by advacher, aluslu.*

# 🧩 Maze Generator Module

This standalone module provides `MazeGenerator` class capable of creating and solving mazes (perfect or non-perfect) using different algorithms. It is designed to be easily imported into any future Python project.

---

## 1. How to Instantiate and Use the Generator

To use the generator, ensure the module is in your project directory and import the `MazeGenerator` class. The generation happens automatically upon instantiation by providing a configuration file.

### Basic Example

```python
from mazegen import MazeGenerator

# 1. Instantiate the generator with a config file
maze = MazeGenerator("config.txt")

# 2. Access the generated grid
grid: list[list[int]] = maze.maze_grid

# 3. Solve the maze and get the path
path: str | None = maze.solve()

print(f"Path to exit: {path}")
```
Once generated and solved, you can use any visual library of your choice to visualize the maze.

## 2. Passing Custom Parameters

Custom parameters (such as size, seed, entry, and exit points) are passed to the generator via a config_parser.

You have to creat a config.txt file with one KEY=VALUE pair per line. 

Lines starting with # are treated as comments and are ignored.

**Mandatory Keys**  

WIDTH	Horizontal size of the maze	Integer ≥2  
HEIGHT	Vertical size of the maze	Integer ≥2  
ENTRY	Starting point coordinates	Must be different from EXIT  
EXIT	Ending point coordinates	Must be different from ENTRY  
OUTPUT_FILE	Path to save the result	Must be in the format *.txt  

    Note on the '42' Pattern: If your maze dimensions are ≥9 in width and ≥7 in height, a special '42' pattern is automatically generated. You must ensure that your ENTRY and EXIT points do not overlap with the points making up this pattern.

Optional Keys

    SEED: (e.g., SEED=42) Can be any string. Used to reproduce specific maze layouts.

    ALGORITHM: Defines the generation logic.

        DFS (Default): Generates long corridors, resulting in a longer path to the exit.

        PRIM: Generates many smaller corridors, resulting in a shorter path to the exit.


## 3. Accessing the Generated Structure

Once the MazeGenerator is instantiated, the actual maze structure is accessible via the maze_grid attribute.
```python

grid: list[list[int]] = maze.maze_grid
```

The grid contains integers ranging from 0 to 15. These integers represent the walls of each cell using a bitmask system. Each number represents the sum of the directions that have a wall:
Value	Direction	Bit Representation

[1]	NORTH	0001

[2]	EAST	0010

[4]	SOUTH	0100

[8]	WEST	1000

Example: 

    If a cell has a value of 15, it has 4 walls.

    If a cell has a value of 8, it has exactly 1 wall located to the West.

    If a cell has a value of 9 (8+1), it has walls on the West and North sides.

## 4. Accessing the Solution

To retrieve the path from the ENTRY to the EXIT, use the solve() method on your instantiated object. It requires no parameters, as it uses the data already parsed from your configuration file.

```python
solved_path: str | None = maze.solve()
```


The method returns a string path if found (None if not found) of cardinal directions representing the exact path to the exit:

    N = NORTH

    S = SOUTH

    E = EAST

    W = WEST

Example Output:

    "NWSENNES"


## 5. Error handling
If you want nice error handling in your project, import these.
It is because Pydantic returns a specific type error which is structured differently.
Also our module has its proper type of error which is MazeConfigParserError

```python
from mazegen import MazeConfigParserError,
from pydantic import ValidationError
```

Then you can wrap the instantiation and the solver in a try except like this:
```python
    try:
        maze: MazeGenerator = MazeGenerator(config_file_name)
        maze.solve()

    except MazeConfigParserError as err:
        sys.stderr.write(f"{err.__class__.__name__, err}")
    except ValidationError as err:
        for error in err.errors():
            field_path = " -> ".join(map(str, error["loc"])).upper()
            field = field_path if field_path else "validate_config"
            msg: str = error.get("msg", "empty")
            sys.stderr.write(f"MazeConfig error, Field {field} : {msg}")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Error: -> {e}\n")
        sys.exit(1)
```
