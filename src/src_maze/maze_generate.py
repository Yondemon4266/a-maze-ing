import random


class MazeGenerator:
    def __init__(self, config_data: dict):
        self.config_data = config_data
        self.width = config_data["WIDTH"]
        self.height = config_data["HEIGHT"]
        self.entry = config_data["ENTRY"]
        self.exit = config_data["EXIT"]

        self.maze_grid = self.initialize_maze()
        self.visited_grid = self.generate_visited_grid()

    def generate_visited_grid(self) -> list[list[bool]]:
        return [[False] * self.width for _ in range(self.height)]

    def initialize_maze(self) -> list[list[int]]:
        return [[15] * self.width for _ in range(self.height)]

    def generate_maze(self) -> None:
        stack: list[tuple] = []

        entry_x, entry_y = self.config_data["ENTRY"]
        self.visited_grid[entry_x][entry_y] = True
        stack.append((entry_x, entry_y))

        while stack:
            current_x, current_y = stack[-1]
            valid_neighbors: list = []

            if (current_x - 1 >= 0 and
                    self.visited_grid[current_x - 1][current_y] is False):
                valid_neighbors.append(("North", current_x - 1, current_y))
            if (current_x + 1 < self.height and
                    self.visited_grid[current_x + 1][current_y] is False):
                valid_neighbors.append(("South", current_x + 1, current_y))
            if (current_y + 1 < self.width and
                    self.visited_grid[current_x][current_y + 1] is False):
                valid_neighbors.append(("East", current_x, current_y + 1))
            if (current_y - 1 >= 0 and
                    self.visited_grid[current_x][current_y - 1] is False):
                valid_neighbors.append(("West", current_x, current_y - 1))

            if valid_neighbors:
                chosen_direction, next_x, next_y = (
                    random.choice(valid_neighbors))

                self.visited_grid[next_x][next_y] = True
                stack.append((next_x, next_y))
                if chosen_direction == "North":
                    self.maze_grid[current_x][current_y] -= 1
                    self.maze_grid[next_x][next_y] -= 4
                elif chosen_direction == "South":
                    self.maze_grid[current_x][current_y] -= 4
                    self.maze_grid[next_x][next_y] -= 1
                elif chosen_direction == "East":
                    self.maze_grid[current_x][current_y] -= 2
                    self.maze_grid[next_x][next_y] -= 8
                else:
                    self.maze_grid[current_x][current_y] -= 8
                    self.maze_grid[next_x][next_y] -= 2
            else:
                stack.pop()
