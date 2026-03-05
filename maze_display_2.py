import mlx
from typing import Any, Callable
from mazegen.maze_generate import MazeGenerator


class DisplayMaze:
    def __init__(self, maze: MazeGenerator):
        self.maze: MazeGenerator = maze
        self.mlx_app = mlx.Mlx()
        self.mlx_ptr = self.mlx_app.mlx_init()
        _, self.screen_width, self.screen_height = (
            self.mlx_app.mlx_get_screen_size(self.mlx_ptr)
        )
        self.win_ptr = self.mlx_app.mlx_new_window(
            self.mlx_ptr,
            self.screen_width,
            self.screen_height,
            "Maze Display",
        )
        self.menu_height = self.screen_height // 8
        self.cell_size = self.calculate_best_cell_size()
        self.maze_width_px = maze.config.width * self.cell_size
        self.maze_height_px = maze.config.height * self.cell_size
        self.maze_img_ptr = self.mlx_app.mlx_new_image(
            self.mlx_ptr, self.maze_width_px, self.maze_height_px
        )
        self.maze_img_data, self.bpp, self.size_line, _ = (
            self.mlx_app.mlx_get_data_addr(self.maze_img_ptr)
        )
        self.bytes_per_pixel = self.bpp // 8

    def calculate_best_cell_size(self):
        margin = 50
        available_maze_width = self.screen_width - (margin * 2)
        available_maze_height = (
            self.screen_height - self.menu_height - (margin * 2)
        )
        size_x = available_maze_width // self.maze.config.width
        size_y = available_maze_height // self.maze.config.height
        cell_size = max(1, min(size_x, size_y))
        return cell_size

    def put_pixel(self, x: int, y: int, color: int):
        """Place un pixel aux coordonnées (x, y)."""
        # Index = (Y * octets_par_ligne) + (X * octets_per_pixel)
        idx = (y * self.size_line) + (x * self.bytes_per_pixel)

        # Format ARGB (Little Endian : B, G, R, A)
        self.maze_img_data[idx] = color & 0xFF  # Bleu
        self.maze_img_data[idx + 1] = (color >> 8) & 0xFF  # Vert
        self.maze_img_data[idx + 2] = (color >> 16) & 0xFF  # Rouge
        self.maze_img_data[idx + 3] = (color >> 24) & 0xFF  # Alpha

    def draw_h_line(self, x: int, y: int, length: int, color: int) -> None:
        """Dessine une ligne horizontale (très rapide)."""
        for i in range(length):
            self.put_pixel(x + i, y, color)

    def draw_v_line(self, x: int, y: int, length: int, color: int) -> None:
        """Dessine une ligne verticale."""
        for i in range(length):
            self.put_pixel(x, y + i, color)

    def draw_rect(
        self, x: int, y: int, width: int, height: int, color: int
    ) -> None:
        """Draw a filled rectangle into the image buffer."""
        for i in range(height):
            self.draw_h_line(x, y + i, width, color)

    def fill_maze(self):
        maze_wall_color = 0xFF00FF00  # Vert
        for row in range(self.maze.config.height):
            for col in range(self.maze.config.width):
                px, py = col * self.cell_size, row * self.cell_size
                val = self.maze.maze_grid[row][col]

                if val & 1:
                    self.draw_h_line(px, py, self.cell_size, maze_wall_color)
                if val & 2:
                    self.draw_v_line(px + self.cell_size - 1, py, self.cell_size, maze_wall_color)
                if val & 4:
                    self.draw_h_line(px, py + self.cell_size - 1, self.cell_size, maze_wall_color)
                if val & 8:
                    self.draw_v_line(px, py, self.cell_size, maze_wall_color)
    
    def put_image_in_center_window(self, width: int, height: int, img):
        start_x = (self.screen_width - width) // 2
        start_y = (self.screen_height - height - self.menu_height) // 2
        self.mlx_app.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, img, start_x, start_y
        )
        
    def key_hook(self, keycode: int) -> int:
        # 65307 'Echap' sous Linux et 53 sous macOS
        # 113 'q'
        if keycode in (53, 65307, 113):
            print("Fermeture demandée...")
            self.mlx_app.mlx_loop_exit(self.mlx_ptr)
        return 0


    def close_hook(self) -> int:
        self.mlx_app.mlx_loop_exit(self.mlx_ptr)
        return 0


# def draw_dynamic(
#     maze: MazeGenerator,
# ) -> None:
#     """Render animated elements: "42" pattern twinkle and path."""
#     # --- "42" pattern twinkle ---
#     if maze.can_fit_pattern():
#         twinkle_idx = (param["frame_count"] // 8) % len(
#             param["pattern_colors"]
#         )
#         current_pattern_color = param["pattern_colors"][twinkle_idx]
#         for row in range(maze.config.height):
#             for col in range(maze.config.width):
#                 if maze.maze_grid[row][col] == 15:
#                     px = col * cell_size
#                     py = row * cell_size
#                     draw_rect(
#                         px,
#                         py,
#                         cell_size,
#                         cell_size,
#                         current_pattern_color,
#                     )

#     # --- Solution path animation ---
#     solution_path: str | None = param["solution"]
#     if param["show_path"] and solution_path:
#         path_coords = []
#         curr_y, curr_x = maze.config.entry

#         if isinstance(solution_path, str):
#             moves = {
#                 "N": (-1, 0),
#                 "S": (1, 0),
#                 "E": (0, 1),
#                 "W": (0, -1),
#             }
#             for move in solution_path:
#                 dy, dx = moves[move]
#                 curr_y += dy
#                 curr_x += dx
#                 path_coords.append((curr_x, curr_y))
#         else:
#             path_coords = [(px, py) for (py, px) in solution_path]

#         param["path_progress"] += 5
#         limite = min(param["path_progress"], len(path_coords))
#         path_animate = path_coords[:limite]

#         for px, py in path_animate:
#             if (py, px) not in (maze.config.entry, maze.config.exit):
#                 draw_rect(
#                     px * cell_size + 4,
#                     py * cell_size + 4,
#                     max(1, cell_size - 8),
#                     max(1, cell_size - 8),
#                     param["path_color"],
#                 )


# def setup_draw_utils(
#     img_data, bpp, size_line
# ) -> tuple[Callable, Callable, Callable, Callable]:
#     bytes_per_pixel = bpp // 8

#     def put_pixel(x: int, y: int, color: int):
#         """Place un pixel aux coordonnées (x, y)."""
#         # Index = (Y * octets_par_ligne) + (X * octets_per_pixel)
#         idx = (y * size_line) + (x * bytes_per_pixel)

#         # Format ARGB (Little Endian : B, G, R, A)
#         img_data[idx] = color & 0xFF  # Bleu
#         img_data[idx + 1] = (color >> 8) & 0xFF  # Vert
#         img_data[idx + 2] = (color >> 16) & 0xFF  # Rouge
#         img_data[idx + 3] = (color >> 24) & 0xFF  # Alpha

#     def draw_h_line(x: int, y: int, length: int, color: int) -> None:
#         """Dessine une ligne horizontale (très rapide)."""
#         for i in range(length):
#             put_pixel(x + i, y, color)

#     def draw_v_line(x: int, y: int, length: int, color: int) -> None:
#         """Dessine une ligne verticale."""
#         for i in range(length):
#             put_pixel(x, y + i, color)

#     def draw_rect(x: int, y: int, width: int, height: int, color: int) -> None:
#         """Draw a filled rectangle into the image buffer."""
#         for i in range(height):
#             draw_h_line(x, y + i, width, color)

#     return (draw_h_line, draw_v_line, draw_rect, put_pixel)


# def put_image_in_center_window(
#     context,
#     screen_height: int,
#     screen_width: int,
#     width: int,
#     height: int,
#     menu_height: int,
# ):
#     mlx_app = context["mlx_app"]
#     mlx_ptr = context["mlx_ptr"]
#     win_ptr = context["win_ptr"]
#     maze_img_ptr = context["maze_img_ptr"]
#     start_x = (screen_width - width) // 2
#     start_y = (screen_height - height - menu_height) // 2
#     mlx_app.mlx_put_image_to_window(
#         mlx_ptr, win_ptr, maze_img_ptr, start_x, start_y
#     )


# def fill_maze(
#     maze: MazeGenerator,
#     cell_size: int,
#     draw_h_line: Callable,
#     draw_v_line: Callable,
# ):
#     maze_wall_color = 0xFF00FF00  # Vert
#     for row in range(maze.config.height):
#         for col in range(maze.config.width):
#             px, py = col * cell_size, row * cell_size
#             val = maze.maze_grid[row][col]

#             if val & 1:
#                 draw_h_line(px, py, cell_size, maze_wall_color)
#             if val & 2:
#                 draw_v_line(px + cell_size - 1, py, cell_size, maze_wall_color)
#             if val & 4:
#                 draw_h_line(px, py + cell_size - 1, cell_size, maze_wall_color)
#             if val & 8:
#                 draw_v_line(px, py, cell_size, maze_wall_color)


# def calculate_best_cell_size(
#     screen_width: int,
#     screen_height: int,
#     menu_height: int,
#     maze: MazeGenerator,
# ):
#     margin = 50
#     available_maze_width = screen_width - (margin * 2)
#     available_maze_height = screen_height - menu_height - (margin * 2)
#     size_x = available_maze_width // maze.config.width
#     size_y = available_maze_height // maze.config.height
#     cell_size = max(1, min(size_x, size_y))
#     return cell_size


def display_2(maze: MazeGenerator):
    display_maze = DisplayMaze(maze)
