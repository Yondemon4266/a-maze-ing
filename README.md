*This project has been created as part of the 42 curriculum by advacher, aluslu.*


Description

[Provide a clear presentation of the project, including its goal and a brief overview.] 
Instructions

[Detail any relevant information about compilation, installation, and/or execution of the program.] 
Configuration File Format

[Explain the complete structure and format of your config file.] 
Maze Generation Algorithm

    Algorithm Chosen: [Name the maze generation algorithm you implemented.] 

    Reasoning: [Explain exactly why you chose this specific algorithm.] 

Code Reusability

    Reusable Parts: [Explain what part of your code is reusable, and how.] 

    Instantiation: [Provide a basic example of how to instantiate and use your generator.] 

    Parameters: [Explain how to pass custom parameters like size and seed.] 

    Accessing Data: [Explain how to access the generated maze structure and at least one solution.] 

Team and Project Management

    Roles: [Define the roles of each team member.] 

    Planning: [Describe your anticipated planning and how it evolved by the end of the project.] 

    Retrospective: [Discuss what worked well and what could be improved.] 

    Tools: [List any specific tools you used during development.] 

Advanced Features

[If you implemented advanced features such as multiple algorithms or extra display options, describe them here. If not, you can remove this section.] 
Resources & AI Usage

    References: [List classic references related to the topic, such as documentation, articles, or tutorials.] 

    AI Assistance: [Describe how AI was used, specifically detailing which tasks and which parts of the project it helped with.]



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