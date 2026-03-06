import mlx
from typing import Any
from enum import Enum
from mazegen.maze_generate import MazeGenerator


class KeyBind(Enum):
    """Enumeration of keyboard key codes for Mac and X11 platforms.

    Each member maps a logical action to a tuple of platform-specific
    key codes that can trigger it.

    Attributes:
        QUIT: Key codes for quitting (Esc, Q).
        NEW_MAZE: Key codes for generating a new maze (Space).
        TOGGLE_PATH: Key codes for toggling the solution path (P).
        THEME: Key codes for cycling the color theme (C).
    """

    QUIT = (53, 65307, 113)  # Esc, Q
    NEW_MAZE = (32, 49)  # Space
    TOGGLE_PATH = (112, 35)  # P
    THEME = (99, 8)  # C


class DisplayMaze:
    """Interactive maze visualizer using the MLX graphics library.

    Renders a maze to a full-screen window with animated solution path,
    a twinkling '42' pattern overlay, and keyboard-driven controls for
    regeneration, theme cycling, and path toggling.

    Attributes:
        maze: The maze generator instance providing grid data and config.
        mlx_app: MLX library interface object.
        mlx_ptr: Pointer to the MLX connection.
        win_ptr: Pointer to the display window.
        screen_width: Width of the screen in pixels.
        screen_height: Height of the screen in pixels.
        state: Dictionary holding runtime display state (colors, flags, etc.).
        menu_height: Pixel height reserved for the bottom UI text area.
        cell_size: Pixel size of each maze cell (square).
        maze_width_px: Total maze image width in pixels.
        maze_height_px: Total maze image height in pixels.
        maze_img_ptr: Pointer to the MLX image buffer for the maze.
        maze_img_data: Raw pixel data buffer of the maze image.
        bpp: Bits per pixel of the image.
        size_line: Number of bytes per image row (stride).
        bytes_per_pixel: Number of bytes per pixel.
    """

    def __init__(self, maze: MazeGenerator):
        """Initialize the display, open the window, and start the event loop.

        Args:
            maze: A fully generated MazeGenerator instance to visualize.
        """
        self.maze: MazeGenerator = maze

        self._init_mlx_and_window()

        self._init_state(maze)

        self._init_dimensions_and_buffers(maze)

        self._static_cache: bytes | None = None
        self._needs_rebuild = True

        self.mlx_app.mlx_hook(self.win_ptr, 33, 0, self.close_hook, self)
        self.mlx_app.mlx_key_hook(self.win_ptr, self.key_hook, self)

        self.mlx_app.mlx_loop_hook(self.mlx_ptr, self.render_loop, self.state)
        self.mlx_app.mlx_loop(self.mlx_ptr)

        self.mlx_app.mlx_destroy_window(self.mlx_ptr, self.win_ptr)

    def _init_mlx_and_window(self) -> None:
        """Initialize the MLX connection, query screen size, and open a window.

        Creates the MLX instance, obtains a connection pointer, queries
        the display resolution, and opens a full-screen window.
        """
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
        """Initialize the mutable runtime state dictionary.

        Sets up colors, flags, and animation counters used during
        rendering and user interaction.

        Args:
            maze: The maze generator, used to obtain the solved path.
        """
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
        """Compute pixel dimensions and create the MLX image buffer.

        Calculates the menu height, optimal cell size, total maze
        pixel dimensions, and allocates the image buffer used for
        all drawing operations.

        Args:
            maze: The maze generator, used to read grid dimensions.
        """
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
        """Calculate the largest cell size that fits the maze on screen.

        Accounts for screen margins and the reserved menu area to
        ensure the entire maze is visible.

        Returns:
            The optimal cell size in pixels (minimum 1).
        """
        margin: int = 50
        available_maze_width: int = self.screen_width - (margin * 2)
        available_maze_height: int = (
            self.screen_height - self.menu_height - (margin * 2)
        )
        size_x: int = available_maze_width // self.maze.config.width
        size_y: int = available_maze_height // self.maze.config.height
        return max(1, min(size_x, size_y))

    def draw_h_line(self, x: int, y: int, cell_size: int, color: int) -> None:
        """Draw a horizontal line of pixels into the image buffer.

        Args:
            x: Starting x-coordinate in pixels.
            y: Y-coordinate (row) in pixels.
            cell_size: Length of the line in pixels.
            color: 32-bit ARGB color value.
        """
        if cell_size <= 0:
            return
        b1, b2, b3, b4 = (
            color & 0xFF,
            (color >> 8) & 0xFF,
            (color >> 16) & 0xFF,
            (color >> 24) & 0xFF,
        )
        row_bytes = bytes([b1, b2, b3, b4]) * cell_size
        start = y * self.size_line + x * self.bytes_per_pixel
        self.maze_img_data[start:start + len(row_bytes)] = row_bytes

    def draw_v_line(self, x: int, y: int, cell_size: int, color: int) -> None:
        """Draw a vertical line of pixels into the image buffer.

        Args:
            x: X-coordinate (column) in pixels.
            y: Starting y-coordinate in pixels.
            cell_size: Length of the line in pixels.
            color: 32-bit ARGB color value.
        """
        for i in range(cell_size):
            idx = ((y + i) * self.size_line) + (x * self.bytes_per_pixel)
            self.maze_img_data[idx] = color & 0xFF
            self.maze_img_data[idx + 1] = (color >> 8) & 0xFF
            self.maze_img_data[idx + 2] = (color >> 16) & 0xFF
            self.maze_img_data[idx + 3] = (color >> 24) & 0xFF

    def draw_rect(
        self, x: int, y: int, cell_size: int, height: int, color: int
    ) -> None:
        """Draw a filled rectangle into the image buffer.

        Args:
            x: Top-left x-coordinate in pixels.
            y: Top-left y-coordinate in pixels.
            cell_size: Width of the rectangle in pixels.
            height: Height of the rectangle in pixels.
            color: 32-bit ARGB color value.
        """
        for i in range(height):
            self.draw_h_line(x, y + i, cell_size, color)

    def clear_image(self, color: int = 0xFF000000) -> None:
        """Fill the entire image buffer with a single color.

        Args:
            color: 32-bit ARGB color value. Defaults to opaque black.
        """
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
            self.maze_img_data[start:start + len(row)] = row

    def restore_from_cache(self) -> None:
        """Restore the image buffer from the cached static maze snapshot.

        Copies the previously cached static frame back into the image
        buffer so that dynamic elements can be redrawn on a clean base.
        """
        if self._static_cache is not None:
            self.maze_img_data[: len(self._static_cache)] = self._static_cache

    def fill_maze(self) -> None:
        """Render the full static maze frame and cache it.

        Clears the image, draws all walls and entry/exit markers,
        then stores the result in ``_static_cache`` so subsequent
        frames can cheaply restore the static base.
        """
        self.clear_image(self.state["bg_color"])
        wall_color = self.state["wall_colors"][self.state["color_theme_idx"]]

        self._draw_walls(wall_color)
        self._draw_entry_exit_markers()

        self._static_cache = bytes(self.maze_img_data)
        self._needs_rebuild = False

    def _draw_walls(self, wall_color: int) -> None:
        """Draw all maze walls based on the grid's bitmask values.

        Iterates over every cell and draws top (bit 0), right (bit 1),
        bottom (bit 2), and left (bit 3) walls as appropriate.

        Args:
            wall_color: 32-bit ARGB color used for wall lines.
        """
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
        """Draw colored rectangles at the maze entry and exit cells.

        Uses ``entry_color`` for the start cell and ``exit_color``
        for the goal cell, with a small inset from cell edges.
        """
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

    def draw_dynamic(self) -> None:
        """Draw all dynamic (per-frame) overlays on top of the cached base.

        Includes the twinkling '42' pattern and the animated solution
        path progression.
        """
        self._draw_twinkle_pattern()
        self._draw_path_animation()

    def _draw_twinkle_pattern(self) -> None:
        """Render the twinkling '42' pattern overlay.

        Cells with a bitmask value of 15 (all walls, i.e. pattern
        cells) are filled with a color that cycles through
        ``pattern_colors`` every 8 frames, creating a sparkle effect.
        Skipped if the maze is too small to fit the pattern.
        """
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
        """Animate the solution path from entry to exit.

        Converts the solution (either a direction string like
        ``"NNESE..."`` or a list of coordinates) into pixel
        positions and progressively reveals one more step each
        frame. Does nothing when the path display is toggled off
        or no solution exists.
        """
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

    def draw_ui(self) -> None:
        """Draw the keyboard shortcut hints below the maze.

        Renders text labels for Space, P, C, and Q/Esc actions,
        horizontally centered beneath the maze image.
        """
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
            start_x + 185,
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

    def put_image_in_center_window(
        self, width: int, height: int, img: Any
    ) -> None:
        """Blit the maze image to the center of the window.

        Args:
            width: Width of the image in pixels.
            height: Height of the image in pixels.
            img: MLX image pointer to display.
        """
        start_x = (self.screen_width - width) // 2
        start_y = (self.screen_height - height - self.menu_height) // 2
        self.mlx_app.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, img, start_x, start_y
        )

    def key_hook(self, keycode: int, param: Any) -> int:
        """Handle keyboard input events.

        Dispatches key codes to the corresponding actions: quit,
        regenerate maze, toggle solution path, or cycle color theme.

        Args:
            keycode: Platform-specific key code of the pressed key.
            param: User-defined parameter passed by MLX (unused).

        Returns:
            Always 0 (required by MLX hook contract).
        """
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
        """Handle the window close event.

        Signals the MLX event loop to exit gracefully.

        Args:
            param: User-defined parameter passed by MLX (unused).

        Returns:
            Always 0 (required by MLX hook contract).
        """
        self.mlx_app.mlx_loop_exit(self.mlx_ptr)
        return 0

    def render_loop(self, param: Any) -> int:
        """Main per-frame render callback invoked by the MLX loop.

        Increments the frame counter, rebuilds the static maze
        image when needed, restores the cached base, draws dynamic
        overlays, and blits the final image to the window.

        Args:
            param: User-defined parameter passed by MLX (unused).

        Returns:
            Always 0 (required by MLX hook contract).
        """
        self.state["frame_count"] += 1

        if self._needs_rebuild:
            self.mlx_app.mlx_clear_window(self.mlx_ptr, self.win_ptr)
            self.fill_maze()
            self.draw_ui()
        self.restore_from_cache()
        self.draw_dynamic()

        self.put_image_in_center_window(
            self.maze_width_px, self.maze_height_px, self.maze_img_ptr
        )
        return 0
