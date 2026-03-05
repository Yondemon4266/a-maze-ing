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
        self.state: Any = {
            "show_path": True,
            "color_theme_idx": 0,
            "wall_colors": [0xFF00FF00, 0xFF00FFFF, 0xFFFF00FF],
            "bg_color": 0xFF000000,
            "path_color": 0xFFFFD700,
            "entry_color": 0xFF00FF00,
            "exit_color": 0xFFFF0000,
            "pattern_colors": [0xFF8822CC, 0xFFAA44EE, 0xFFCC88FF, 0xFFAA44EE],
            "frame_count": 0,
            "path_progress": 0,
            "solution": maze.solved_path,
        }

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

        # Cache statique : snapshot du buffer après fill_maze()
        self._static_cache: bytes | None = None
        self._needs_rebuild = True

        self.mlx_app.mlx_hook(self.win_ptr, 33, 0, self.close_hook, self)
        self.mlx_app.mlx_key_hook(self.win_ptr, self.key_hook, self)
        self.mlx_app.mlx_loop_hook(self.mlx_ptr, self.render_loop, self.state)
        self.mlx_app.mlx_loop(self.mlx_ptr)
        self.mlx_app.mlx_destroy_window(self.mlx_ptr, self.win_ptr)

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
        """Dessine une ligne horizontale (bulk write optimisé)."""
        if length <= 0:
            return
        b1 = color & 0xFF
        b2 = (color >> 8) & 0xFF
        b3 = (color >> 16) & 0xFF
        b4 = (color >> 24) & 0xFF
        row_bytes = bytes([b1, b2, b3, b4]) * length
        start = y * self.size_line + x * self.bytes_per_pixel
        self.maze_img_data[start : start + len(row_bytes)] = row_bytes

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

    def clear_image(self, color: int = 0xFF000000) -> None:
        """Efface tout le buffer image avec la couleur donnée.

        Utilise un bulk write ligne par ligne via size_line
        (comme recommandé par la doc MiniLibX pour l'alignement).
        """
        b1 = color & 0xFF
        b2 = (color >> 8) & 0xFF
        b3 = (color >> 16) & 0xFF
        b4 = (color >> 24) & 0xFF
        pixel = bytes([b1, b2, b3, b4])
        row = pixel * self.maze_width_px
        for y in range(self.maze_height_px):
            start = y * self.size_line
            self.maze_img_data[start : start + len(row)] = row

    def restore_from_cache(self) -> None:
        """Restaure le buffer image depuis le cache statique."""
        if self._static_cache is not None:
            self.maze_img_data[: len(self._static_cache)] = self._static_cache

    def fill_maze(self):
        """Dessine les murs, entrée et sortie. Met à jour le cache."""
        self.clear_image(self.state["bg_color"])
        wall_color = self.state["wall_colors"][self.state["color_theme_idx"]]
        for row in range(self.maze.config.height):
            for col in range(self.maze.config.width):
                px, py = col * self.cell_size, row * self.cell_size
                val = self.maze.maze_grid[row][col]

                if val & 1:
                    self.draw_h_line(px, py, self.cell_size, wall_color)
                if val & 2:
                    self.draw_v_line(
                        px + self.cell_size - 1,
                        py,
                        self.cell_size,
                        wall_color,
                    )
                if val & 4:
                    self.draw_h_line(
                        px,
                        py + self.cell_size - 1,
                        self.cell_size,
                        wall_color,
                    )
                if val & 8:
                    self.draw_v_line(px, py, self.cell_size, wall_color)

        # Entry / Exit markers
        entry_y, entry_x = self.maze.config.entry
        self.draw_rect(
            entry_x * self.cell_size + 2,
            entry_y * self.cell_size + 2,
            max(1, self.cell_size - 4),
            max(1, self.cell_size - 4),
            self.state["entry_color"],
        )
        exit_y, exit_x = self.maze.config.exit
        self.draw_rect(
            exit_x * self.cell_size + 2,
            exit_y * self.cell_size + 2,
            max(1, self.cell_size - 4),
            max(1, self.cell_size - 4),
            self.state["exit_color"],
        )

        # Sauvegarder le cache statique
        self._static_cache = bytes(self.maze_img_data)
        self._needs_rebuild = False

    def put_image_in_center_window(self, width: int, height: int, img):
        start_x = (self.screen_width - width) // 2
        start_y = (self.screen_height - height - self.menu_height) // 2
        self.mlx_app.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, img, start_x, start_y
        )

    def key_hook(self, keycode: int, param: Any) -> int:
        if keycode in (53, 65307, 113):
            self.mlx_app.mlx_loop_exit(self.mlx_ptr)

        elif keycode in (32, 49):  # Space
            self.state["path_progress"] = 0
            self.maze.regenerate()
            self.state["solution"] = self.maze.solve()
            self._needs_rebuild = True

        elif keycode in (112, 35):  # 'p'
            self.state["show_path"] = not self.state["show_path"]
            self.state["path_progress"] = 0

        elif keycode in (99, 8):  # 'c'
            self.state["color_theme_idx"] = (
                self.state["color_theme_idx"] + 1
            ) % len(self.state["wall_colors"])
            self._needs_rebuild = True
        return 0

    def close_hook(self, param: Any) -> int:
        self.mlx_app.mlx_loop_exit(self.mlx_ptr)
        return 0

    def render_loop(self, param: Any) -> int:
        """Main render-loop callback invoked every frame."""
        self.state["frame_count"] += 1

        # Rebuild le cache seulement si l'état a changé (lent)
        if self._needs_rebuild:
            self.fill_maze()

        # Restaure le buffer depuis le cache (quasi instantané)
        self.restore_from_cache()

        # Éléments animés par-dessus le fond statique
        self.draw_dynamic()

        self.put_image_in_center_window(
            self.maze_width_px, self.maze_height_px, self.maze_img_ptr
        )
        return 0

    def draw_dynamic(self) -> None:
        """Render animated elements: "42" pattern twinkle and path."""
        # --- "42" pattern twinkle ---
        if self.maze.can_fit_pattern():
            twinkle_idx = (self.state["frame_count"] // 8) % len(
                self.state["pattern_colors"]
            )
            current_pattern_color = self.state["pattern_colors"][twinkle_idx]
            for row in range(self.maze.config.height):
                for col in range(self.maze.config.width):
                    if self.maze.maze_grid[row][col] == 15:
                        px = col * self.cell_size
                        py = row * self.cell_size
                        self.draw_rect(
                            px,
                            py,
                            self.cell_size,
                            self.cell_size,
                            current_pattern_color,
                        )

        # --- Solution path animation ---
        solution_path: str | None = self.state["solution"]
        if self.state["show_path"] and solution_path:
            path_coords = []
            curr_y, curr_x = self.maze.config.entry

            if isinstance(solution_path, str):
                moves = {
                    "N": (-1, 0),
                    "S": (1, 0),
                    "E": (0, 1),
                    "W": (0, -1),
                }
                for move in solution_path:
                    dy, dx = moves[move]
                    curr_y += dy
                    curr_x += dx
                    path_coords.append((curr_x, curr_y))
            else:
                path_coords = [(px, py) for (py, px) in solution_path]

            self.state["path_progress"] += 1
            limite = min(self.state["path_progress"], len(path_coords))
            path_animate = path_coords[:limite]

            for px, py in path_animate:
                if (py, px) not in (
                    self.maze.config.entry,
                    self.maze.config.exit,
                ):
                    self.draw_rect(
                        px * self.cell_size + 4,
                        py * self.cell_size + 4,
                        max(1, self.cell_size - 8),
                        max(1, self.cell_size - 8),
                        self.state["path_color"],
                    )


def display_2(maze: MazeGenerator):
    display_maze = DisplayMaze(maze)
