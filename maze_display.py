"""Interactive MLX-based graphical display for the generated maze."""

import sys
import mlx
from typing import TypedDict
from mazegen.maze_generate import MazeGenerator


class GameState(TypedDict):
    """Mutable state dictionary passed to MLX hook callbacks.

    Attributes:
        show_path: Whether the solution path is visible.
        color_theme_idx: Index into ``wall_colors`` for the active
            wall colour.
        wall_colors: Available wall colour choices (ARGB integers).
        bg_color: Background colour (ARGB).
        path_color: Solution-path colour (ARGB).
        entry_color: Entry-cell highlight colour (ARGB).
        exit_color: Exit-cell highlight colour (ARGB).
        pattern_colors: Colours cycled for the "42" pattern twinkle
            animation.
        drawn: Whether the static UI text has been drawn since the
            last state change.
        frame_count: Running frame counter used for animation timing.
        path_progress: Number of path segments currently animated.
        solution: Direction string for the solved path, or ``None``.
    """

    show_path: bool
    color_theme_idx: int
    wall_colors: list[int]
    bg_color: int
    path_color: int
    entry_color: int
    exit_color: int
    pattern_colors: list[int]
    drawn: bool
    frame_count: int
    path_progress: int
    solution: str | None


def display_maze(maze: MazeGenerator) -> None:
    """Open an MLX window and render the maze interactively.

    Creates a window sized to the maze, registers keyboard and
    render-loop hooks, and enters the MLX event loop.  The user can
    toggle the solution path, cycle wall colours, regenerate the maze,
    or quit via keyboard shortcuts displayed in a side UI panel.

    Args:
        maze: A fully generated and solved ``MazeGenerator`` instance.
    """

    mlx_app = mlx.Mlx()
    mlx_ptr = mlx_app.mlx_init()
    if not mlx_ptr:
        sys.stderr.write("Error: Failed to initialize MLX.\n")
        return

    _, screen_width, screen_height = mlx_app.mlx_get_screen_size(mlx_ptr)

    ui_width: int = 250  # UI

    max_cell_width: int = (screen_width - ui_width) // maze.config.width
    max_cell_height: int = screen_height // maze.config.height
    cell_size: int = max(1, min(20, max_cell_width, max_cell_height))  # Pixels

    maze_width_px: int = maze.config.width * cell_size
    win_width: int = maze_width_px + ui_width
    win_height: int = maze.config.height * cell_size

    win_width = min(win_width, screen_width)
    win_height = min(win_height, screen_height)

    win_ptr = mlx_app.mlx_new_window(
        mlx_ptr, win_width, win_height, "A-Maze-ing"
    )

    # Memory image creation for fast rendering.
    img_ptr = mlx_app.mlx_new_image(mlx_ptr, maze_width_px, win_height)
    img_data, bpp, size_line, endian = mlx_app.mlx_get_data_addr(img_ptr)
    bytes_per_pixel = bpp // 8

    # State Management for Interactions
    state: GameState = {
        "show_path": True,
        "color_theme_idx": 0,
        "wall_colors": [0xFF00FF00, 0xFF00FFFF, 0xFFFF00FF],
        "bg_color": 0xFF000000,
        "path_color": 0xFFFFD700,
        "entry_color": 0xFF00FF00,
        "exit_color": 0xFFFF0000,
        "pattern_colors": [0xFF8822CC, 0xFFAA44EE, 0xFFCC88FF, 0xFFAA44EE],
        "drawn": False,
        "frame_count": 0,
        "path_progress": 0,
        "solution": maze.solved_path,
    }

    def draw_h_line(x: int, y: int, length: int, color: int) -> None:
        """Draw a horizontal line into the image buffer.

        Args:
            x: Starting x pixel coordinate.
            y: Y pixel coordinate (row).
            length: Number of pixels to draw.
            color: ARGB colour integer.
        """
        if not (0 <= y < win_height) or x >= maze_width_px:
            return

        # Truncate if line exceeds window bounds.
        if x < 0:
            length += x
            x = 0
        if x + length > maze_width_px:
            length = maze_width_px - x
        if length <= 0:
            return

        # Prepare 4-byte pixel (Little Endian).
        b1 = color & 0xFF
        b2 = (color >> 8) & 0xFF
        b3 = (color >> 16) & 0xFF
        b4 = (color >> 24) & 0xFF

        # Batch-multiply bytes to generate full line.
        row_bytes = bytes([b1, b2, b3, b4]) * length

        start_idx = (y * size_line) + (x * bytes_per_pixel)
        end_idx = start_idx + (length * bytes_per_pixel)

        # Bulk memory replacement.
        img_data[start_idx:end_idx] = row_bytes

    def draw_v_line(x: int, y: int, length: int, color: int) -> None:
        """Draw a vertical line into the image buffer.

        Args:
            x: X pixel coordinate (column).
            y: Starting y pixel coordinate.
            length: Number of pixels to draw.
            color: ARGB colour integer.
        """
        if not (0 <= x < maze_width_px) or y >= win_height:
            return

        if y < 0:
            length += y
            y = 0
        if y + length > win_height:
            length = win_height - y
        if length <= 0:
            return

        b1 = color & 0xFF
        b2 = (color >> 8) & 0xFF
        b3 = (color >> 16) & 0xFF
        b4 = (color >> 24) & 0xFF

        idx = (y * size_line) + (x * bytes_per_pixel)
        max_idx = len(img_data)

        for _ in range(length):
            if idx + 3 < max_idx:
                img_data[idx] = b1
                img_data[idx + 1] = b2
                img_data[idx + 2] = b3
                img_data[idx + 3] = b4
            idx += size_line

    def draw_rect(x: int, y: int, width: int, height: int, color: int) -> None:
        """Draw a filled rectangle into the image buffer.

        Args:
            x: Top-left x pixel coordinate.
            y: Top-left y pixel coordinate.
            width: Rectangle width in pixels.
            height: Rectangle height in pixels.
            color: ARGB colour integer.
        """
        for i in range(height):
            draw_h_line(x, y + i, width, color)

    def draw_static() -> None:
        """Render static maze elements.

        Draws the background, cell walls, entry marker, and exit
        marker into the image buffer.
        """
        draw_rect(0, 0, maze_width_px, win_height, state["bg_color"])

        current_wall_color = state["wall_colors"][state["color_theme_idx"]]

        for row in range(maze.config.height):
            for col in range(maze.config.width):
                cell_val = maze.maze_grid[row][col]
                px = col * cell_size
                py = row * cell_size

                if cell_val & 1:  # North
                    draw_h_line(px, py, cell_size, current_wall_color)
                if cell_val & 2:  # East
                    draw_v_line(
                        px + cell_size - 1, py, cell_size, current_wall_color
                    )
                if cell_val & 4:  # South
                    draw_h_line(
                        px, py + cell_size - 1, cell_size, current_wall_color
                    )
                if cell_val & 8:  # West
                    draw_v_line(px, py, cell_size, current_wall_color)

        # Entry / Exit
        entry_y, entry_x = maze.config.entry
        draw_rect(
            entry_x * cell_size + 2,
            entry_y * cell_size + 2,
            cell_size - 4,
            cell_size - 4,
            state["entry_color"],
        )

        exit_y, exit_x = maze.config.exit
        draw_rect(
            exit_x * cell_size + 2,
            exit_y * cell_size + 2,
            cell_size - 4,
            cell_size - 4,
            state["exit_color"],
        )

    def draw_dynamic(param: GameState) -> None:
        """Render animated elements: "42" pattern twinkle and path.

        Args:
            param: Current game state dictionary.
        """
        # Animate Pattern
        if maze.can_fit_pattern():
            twinkle_idx = (param["frame_count"] // 8) % len(
                param["pattern_colors"]
            )
            current_pattern_color = param["pattern_colors"][twinkle_idx]

            for row in range(maze.config.height):
                for col in range(maze.config.width):
                    if maze.maze_grid[row][col] == 15:
                        px = col * cell_size
                        py = row * cell_size
                        draw_rect(
                            px, py, cell_size, cell_size, current_pattern_color
                        )

        solution_path: str | None = param["solution"]
        if param["show_path"] and solution_path:
            path_coords = []
            curr_y, curr_x = maze.config.entry

            if isinstance(solution_path, str):
                moves = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}
                for move in solution_path:
                    dy, dx = moves[move]
                    curr_y += dy
                    curr_x += dx
                    path_coords.append((curr_x, curr_y))
            else:
                path_coords = [(px, py) for (py, px) in solution_path]

            param["path_progress"] += 5
            limite = min(param["path_progress"], len(path_coords))
            path_animate = path_coords[:limite]

            for px, py in path_animate:
                if (py, px) not in (maze.config.entry, maze.config.exit):
                    draw_rect(
                        px * cell_size + 4,
                        py * cell_size + 4,
                        max(1, cell_size - 8),
                        max(1, cell_size - 8),
                        param["path_color"],
                    )

    def draw_ui() -> None:
        """Draw the side-panel UI text listing keyboard shortcuts."""
        ui_x = (maze.config.width * cell_size) + 10
        text_color = 0xFFFFFF
        mlx_app.mlx_string_put(
            mlx_ptr, win_ptr, ui_x, 40, text_color, "    === MENU ==="
        )
        mlx_app.mlx_string_put(
            mlx_ptr, win_ptr, ui_x, 80, text_color, "Space  : New maze"
        )
        mlx_app.mlx_string_put(
            mlx_ptr, win_ptr, ui_x, 105, text_color, "P      : Display"
        )
        mlx_app.mlx_string_put(
            mlx_ptr, win_ptr, ui_x, 125, text_color, "         Hide path"
        )
        mlx_app.mlx_string_put(
            mlx_ptr, win_ptr, ui_x, 150, text_color, "C      : Change colors"
        )
        mlx_app.mlx_string_put(
            mlx_ptr, win_ptr, ui_x, 175, text_color, "Q/Esc  : Quit"
        )

    def expose_hook(param: GameState) -> int:
        """Handle window expose events by requesting a redraw.

        Args:
            param: Current game state dictionary.

        Returns:
            ``0`` (required by MLX hook signature).
        """
        param["drawn"] = False  # Demande de redessiner l'UI
        return 0

    def key_hook(keycode: int, param: GameState) -> int:
        """Handle keyboard input for maze interactions.

        Supported keys:
            - **Esc / Q**: Quit the application.
            - **Space**: Regenerate and re-solve the maze.
            - **P**: Toggle solution-path visibility.
            - **C**: Cycle wall colour theme.

        Args:
            keycode: Platform-specific key code.
            param: Current game state dictionary.

        Returns:
            ``0`` (required by MLX hook signature).
        """
        if keycode in (53, 65307, 113):  # Esc or 'q'
            mlx_app.mlx_loop_exit(mlx_ptr)

        elif keycode in (32, 49):  # Space
            param["path_progress"] = 0
            maze.regenerate()
            param["solution"] = maze.solve()
            param["drawn"] = False

        elif keycode in (112, 35):  # 'p'
            param["show_path"] = not param["show_path"]
            param["path_progress"] = 0
            param["drawn"] = False

        elif keycode in (99, 8):  # 'c'
            param["color_theme_idx"] = (param["color_theme_idx"] + 1) % len(
                param["wall_colors"]
            )
            param["drawn"] = False

        return 0

    def render_loop_hook(param: GameState) -> int:
        """Main render-loop callback invoked every frame by MLX.

        Increments the frame counter, redraws static and dynamic
        layers, and composites the image to the window.  When the
        state is dirty (``drawn is False``), also redraws the UI
        text overlay.

        Args:
            param: Current game state dictionary.

        Returns:
            ``0`` (required by MLX hook signature).
        """
        param["frame_count"] += 1

        draw_static()
        draw_dynamic(param)

        mlx_app.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 0, 0)

        if not param["drawn"]:
            mlx_app.mlx_clear_window(mlx_ptr, win_ptr)
            mlx_app.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 0, 0)
            draw_ui()
            param["drawn"] = True

        return 0

    # Register hooks with the state parameter.
    mlx_app.mlx_key_hook(win_ptr, key_hook, state)
    mlx_app.mlx_expose_hook(win_ptr, expose_hook, state)
    mlx_app.mlx_loop_hook(mlx_ptr, render_loop_hook, state)

    # Start the main event loop.
    mlx_app.mlx_loop(mlx_ptr)

    # Clean up resources after exiting the loop.
    mlx_app.mlx_destroy_window(mlx_ptr, win_ptr)
    mlx_app.mlx_release(mlx_ptr)
