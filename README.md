*This project has been created as part of the 42 curriculum by advacher, aluslu.*


# Description

This project is to creat a maze generator in Python that reads from a configuration file to generate a valid maze. The generated maze can optionally be "perfect," meaning it has exactly one unique path between the entry and the exit. The final structure is written to an output file using a hexadecimal representation to map out the walls, and the project also features a visual representation of the generated maze.

## Instructions

The project is built using Python 3.10 or later.

To execute the program, use the following command:
A Makefile is included to automate standard tasks. The available rules are:

    make install: Installs project dependencies.

    make run: Executes the main script.

    make debug: Runs the script in debug mode.

    make clean: Removes temporary files or caches like __pycache__.

    make fclean: Removes clean + .venv 

    make lint: Executes formatting and typing checks using flake8 and mypy

    make lint-strict : Checks using flake8 and mypy whith flag strict

    make build: Creates package src/mazegen module into .whl file

The configuration file dictates the parameters of the maze and uses one KEY=VALUE pair per line. Any line starting with a # is treated as a comment and is ignored.

The following keys must be defined:

    WIDTH: The horizontal size of the maze (number of cells).

    HEIGHT: The vertical size of the maze.

    ENTRY: The entry coordinates, formatted as x,y.

    EXIT: The exit coordinates, formatted as x,y.

    OUTPUT_FILE: The filename where the generated maze data will be saved.

    PERFECT: A boolean flag (e.g., True) defining whether the maze should be perfect.

    SEED: Make the same maze from the seed again and again.

    ALGORITHM: Logical structure of the maze before any visual rendering.


Maze Generation Algorithm

    Algorithms Chosen: 
    
        DFS (Depth-First Search): Used for generating "perfect" mazes with long, winding corridors.

        Prim's Algorithm: Used for generating mazes with a more complex, branching structure and shorter corridors.

        BFS (Breadth-First Search): Used as the Solver to find the shortest path between the entry and exit points.

    Reasoning:

        DFS (Generation): I chose the randomized DFS (Recursive Backtracker) because it is highly efficient and guarantees a perfect maze (one single path between any two points). Its "deep" exploration creates long, challenging paths that are aesthetically pleasing and difficult to solve.

        Prim's (Generation): Prim’s was implemented as a secondary option to provide variety. Unlike DFS, Prim's grows outward from a central point, creating a "sprawl" of shorter dead-ends. This results in a maze that looks more natural and less like a single long tunnel.

        BFS (Solving): For the solver, BFS was the logical choice because it guarantees finding the shortest path in an unweighted grid. While DFS could find a path, BFS explores all possible directions layer by layer, ensuring that the solution returned is the most optimal route to the exit.

Code Reusability

    MazeGenerator Module

    This standalone module generates and solves customizable mazes (perfect or non-perfect) using DFS or Prim's algorithms. It relies on a config.txt file to define parameters like dimensions, entry/exit points, and optional generation seeds.

        Maze Structure: The generated maze is accessed via maze.maze_grid, which returns a 2D grid of integers. These integers use a bitmask system (1=North, 2=East, 4=South, 8=West) to represent cell walls.

        Pathfinding: The .solve() method automatically calculates the route from entry to exit, returning a string of cardinal directions (e.g., "NNESW").

        Error Handling: Built-in support for Pydantic ValidationError and custom MazeConfigParserError ensures safe parsing of your configuration file.

    Quick Start:
    Python

    from mazegen import MazeGenerator

    maze = MazeGenerator("config.txt")
    grid = maze.maze_grid     # 2D list of bitmask wall values
    path = maze.solve()       # Returns direction string or None


Team and Project Management  
Dev A : Aluslu  
Dev B : Advacher

## ⚙️ Phase 1 : Core Logic

* **Dev A (The Parser):** Reads `config.txt`, validates the data (dimensions, characters allowed), and initializes the empty grid/data structure.

* **Dev B (The Algorithm):** Writes the actual maze generation algorithm (e.g., Recursive Backtracking or Prim's). Takes the empty grid and "carves" the paths.

## 🎨 Phase 2: Graphics & MiniLibX (Specialization)

* **Dev A (The Renderer):** Writes the loop that reads the generated grid and calls MiniLibX drawing functions (pixels, squares, colors for walls vs. paths).

* **Dev B (The Controller):** Handles window creation (`mlx_new_window`), hooks/events (pressing `ESC` to quit, clicking the red cross), and ensures clean destruction to prevent memory leaks.  

## 🧠 Phase 3: The Solver (Pathfinding) 

* **Dev A (The Path Renderer):** Updates the graphical engine. Takes the list of winning coordinates from Dev B and draws the solution path on the screen (e.g., drawing a distinct red line or colored squares from the entrance to the exit).
    Roles: [Define the roles of each team member.] 

* **Dev B (The Pathfinder):** Implements the solving algorithm. This function takes the generated grid, finds the start and end points, and returns the list of coordinates that form the winning route. 

Git Workflow & Quality Assurance

We implemented a strict Pull Request (PR)-based workflow to maintain a high-quality codebase and foster team synchronization.

    Feature Isolation: Every feature (DFS, BFS, Rendering) was developed on dedicated branches; we never pushed directly to main.

    The PR Gatekeeper: Each Pull Request served as a mandatory checkpoint. Team members conducted line-by-line reviews to verify subject compliance and logic accuracy.

    Impact: This workflow transformed development into a continuous learning cycle, ensuring that every line of code was understood by the entire team while eliminating technical debt early.

Resources & AI Usage

    References

    Documentation: 42 Docs - MiniLibX - : harm-smits.github.io/42docs/libs/minilibx Essential for understanding the logic of window management and pixel buffers.

    Video Tutorial (DFS-BFS):https://www.youtube.com/watch?v=cS-198wtfj0

    AI Assistance

    AI acted as a conceptual bridge, translating low-level C paradigms (like mlx_pixel_put) into efficient Pythonic structures. 

    Algorithmic Optimization: Identified edge cases for the DFS Recursive Backtracker and managed memory efficiency for the BFS solver queue.

    Data Encoding: Refined the logic for the 4-bit wall encoding system (bitmasking) to ensure data integrity between the generator and the output file.


