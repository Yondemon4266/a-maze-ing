import mlx
from typing import Any
from enum import Enum
from mazegen.maze_generate import MazeGenerator


class KeyBind(Enum):
    """Énumération des codes de touches (Mac / X11)."""

    QUIT = (53, 65307, 113)  # Esc, Q
    NEW_MAZE = (32, 49)  # Space
    TOGGLE_PATH = (112, 35)  # P
    THEME = (99, 8)  # C


class DisplayMaze:

    def __init__(self, maze: MazeGenerator):
        self.maze: MazeGenerator = maze

        # 1. Initialisation de MLX et de la fenêtre
        self._init_mlx_and_window()

        # 2. Initialisation de l'état
        self._init_state(maze)

        # 3. Calcul des dimensions et création du buffer d'image
        self._init_dimensions_and_buffers(maze)

        # 4. Configuration des hooks et lancement
        self._static_cache: bytes | None = None
        self._needs_rebuild = True

        self.mlx_app.mlx_hook(self.win_ptr, 33, 0, self.close_hook, self)
        self.mlx_app.mlx_key_hook(self.win_ptr, self.key_hook, self)
        self.mlx_app.mlx_loop_hook(self.mlx_ptr, self.render_loop, self.state)

        self.mlx_app.mlx_loop(self.mlx_ptr)
        self.mlx_app.mlx_destroy_window(self.mlx_ptr, self.win_ptr)

    # ==========================================
    # INITIALISATION (Factorisation de __init__)
    # ==========================================

    def _init_mlx_and_window(self) -> None:
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

    def _init_state(self, maze: MazeGenerator) -> None:
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

    def _init_dimensions_and_buffers(self, maze: MazeGenerator) -> None:
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

    def calculate_best_cell_size(self) -> int:
        margin: int = 50
        available_maze_width: int = self.screen_width - (margin * 2)
        available_maze_height: int = (
            self.screen_height - self.menu_height - (margin * 2)
        )
        size_x: int = available_maze_width // self.maze.config.width
        size_y: int = available_maze_height // self.maze.config.height
        return max(1, min(size_x, size_y))

    # ==========================================
    # PRIMITIVES DE DESSIN
    # ==========================================

    def put_pixel(self, x: int, y: int, color: int) -> None:
        idx = (y * self.size_line) + (x * self.bytes_per_pixel)
        self.maze_img_data[idx] = color & 0xFF
        self.maze_img_data[idx + 1] = (color >> 8) & 0xFF
        self.maze_img_data[idx + 2] = (color >> 16) & 0xFF
        self.maze_img_data[idx + 3] = (color >> 24) & 0xFF

    def draw_h_line(self, x: int, y: int, length: int, color: int) -> None:
        if length <= 0:
            return
        b1, b2, b3, b4 = (
            color & 0xFF,
            (color >> 8) & 0xFF,
            (color >> 16) & 0xFF,
            (color >> 24) & 0xFF,
        )
        row_bytes = bytes([b1, b2, b3, b4]) * length
        start = y * self.size_line + x * self.bytes_per_pixel
        self.maze_img_data[start : start + len(row_bytes)] = row_bytes

    def draw_v_line(self, x: int, y: int, length: int, color: int) -> None:
        for i in range(length):
            self.put_pixel(x, y + i, color)

    def draw_rect(
        self, x: int, y: int, width: int, height: int, color: int
    ) -> None:
        for i in range(height):
            self.draw_h_line(x, y + i, width, color)

    def clear_image(self, color: int = 0xFF000000) -> None:
        b1, b2, b3, b4 = (
            color & 0xFF,
            (color >> 8) & 0xFF,
            (color >> 16) & 0xFF,
            (color >> 24) & 0xFF,
        )
        pixel = bytes([b1, b2, b3, b4])
        row = pixel * self.maze_width_px
        for y in range(self.maze_height_px):
            start = y * self.size_line
            self.maze_img_data[start : start + len(row)] = row

    def restore_from_cache(self) -> None:
        if self._static_cache is not None:
            self.maze_img_data[: len(self._static_cache)] = self._static_cache

    # ==========================================
    # RENDU DU LABYRINTHE (Factorisation)
    # ==========================================

    def fill_maze(self) -> None:
        self.clear_image(self.state["bg_color"])
        wall_color = self.state["wall_colors"][self.state["color_theme_idx"]]

        self._draw_walls(wall_color)
        self._draw_entry_exit_markers()

        self._static_cache = bytes(self.maze_img_data)
        self._needs_rebuild = False

    def _draw_walls(self, wall_color: int) -> None:
        """Parcourt la grille et dessine les murs statiques."""
        for row in range(self.maze.config.height):
            for col in range(self.maze.config.width):
                px, py = col * self.cell_size, row * self.cell_size
                val = self.maze.maze_grid[row][col]

                if val & 1:
                    self.draw_h_line(px, py, self.cell_size, wall_color)
                if val & 2:
                    self.draw_v_line(
                        px + self.cell_size - 1, py, self.cell_size, wall_color
                    )
                if val & 4:
                    self.draw_h_line(
                        px, py + self.cell_size - 1, self.cell_size, wall_color
                    )
                if val & 8:
                    self.draw_v_line(px, py, self.cell_size, wall_color)

    def _draw_entry_exit_markers(self) -> None:
        """Dessine les points de départ et d'arrivée."""
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

    # ==========================================
    # RENDU DYNAMIQUE (Factorisation)
    # ==========================================

    def draw_dynamic(self) -> None:
        self._draw_twinkle_pattern()
        self._draw_path_animation()

    def _draw_twinkle_pattern(self) -> None:
        """Gère l'affichage du motif clignotant '42'."""
        if not self.maze.can_fit_pattern():
            return

        twinkle_idx = (self.state["frame_count"] // 8) % len(
            self.state["pattern_colors"]
        )
        current_pattern_color = self.state["pattern_colors"][twinkle_idx]

        for row in range(self.maze.config.height):
            for col in range(self.maze.config.width):
                if self.maze.maze_grid[row][col] == 15:
                    px, py = col * self.cell_size, row * self.cell_size
                    self.draw_rect(
                        px,
                        py,
                        self.cell_size,
                        self.cell_size,
                        current_pattern_color,
                    )

    def _draw_path_animation(self) -> None:
        """Gère l'affichage et l'animation du chemin de résolution."""
        solution_path: str | None = self.state["solution"]
        if not (self.state["show_path"] and solution_path):
            return

        path_coords = []
        curr_y, curr_x = self.maze.config.entry

        if isinstance(solution_path, str):
            moves = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}
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
            if (py, px) not in (self.maze.config.entry, self.maze.config.exit):
                self.draw_rect(
                    px * self.cell_size + 4,
                    py * self.cell_size + 4,
                    max(1, self.cell_size - 8),
                    max(1, self.cell_size - 8),
                    self.state["path_color"],
                )

    # ==========================================
    # INTERFACE ET AFFICHAGE MLX
    # ==========================================

    def draw_ui(self) -> None:
        total_text_width = 650
        start_x = (self.screen_width - total_text_width) // 2
        maze_start_y = (
            self.screen_height - self.maze_height_px - self.menu_height
        ) // 2
        text_y = maze_start_y + self.maze_height_px + 50

        self.mlx_app.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            start_x,
            text_y,
            0xFFFFFF,
            "Space: New;",
        )
        self.mlx_app.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            start_x + 200,
            text_y,
            0xFFFFFF,
            "P: Path Solve;",
        )
        self.mlx_app.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            start_x + 400,
            text_y,
            0xFFFFFF,
            "C: Theme;",
        )
        self.mlx_app.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            start_x + 550,
            text_y,
            0xFFFFFF,
            "Q,esc: Quit;",
        )

    def put_image_in_center_window(self, width: int, height: int, img) -> None:
        start_x = (self.screen_width - width) // 2
        start_y = (self.screen_height - height - self.menu_height) // 2
        self.mlx_app.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, img, start_x, start_y
        )

    # ==========================================
    # BOUCLE ET ÉVÉNEMENTS
    # ==========================================

    def key_hook(self, keycode: int, param: Any) -> int:
        # Utilisation de l'Enum pour les vérifications de touches
        if keycode in KeyBind.QUIT.value:
            self.mlx_app.mlx_loop_exit(self.mlx_ptr)

        elif keycode in KeyBind.NEW_MAZE.value:
            self.state["path_progress"] = 0
            self.maze.regenerate()
            self.state["solution"] = self.maze.solve()
            self._needs_rebuild = True

        elif keycode in KeyBind.TOGGLE_PATH.value:
            self.state["show_path"] = not self.state["show_path"]
            self.state["path_progress"] = 0

        elif keycode in KeyBind.THEME.value:
            self.state["color_theme_idx"] = (
                self.state["color_theme_idx"] + 1
            ) % len(self.state["wall_colors"])
            self._needs_rebuild = True

        return 0

    def close_hook(self, param: Any) -> int:
        self.mlx_app.mlx_loop_exit(self.mlx_ptr)
        return 0

    def render_loop(self, param: Any) -> int:
        self.state["frame_count"] += 1

        if self._needs_rebuild:
            self.fill_maze()
            self.draw_ui()

        self.restore_from_cache()
        self.draw_dynamic()

        self.put_image_in_center_window(
            self.maze_width_px, self.maze_height_px, self.maze_img_ptr
        )
        return 0


def display_2(maze: MazeGenerator) -> None:
    display_maze = DisplayMaze(maze)
