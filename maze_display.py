import sys
import mlx
from typing import TypedDict
from mazegen.maze_generate import MazeGenerator


class GameState(TypedDict):
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

    cell_size: int = 20  # Pixels maze
    ui_width: int = 250  # Pixel UI
    win_width: int = (maze.width * cell_size) + ui_width
    win_height: int = maze.height * cell_size

    mlx_app = mlx.Mlx()
    mlx_ptr = mlx_app.mlx_init()
    if not mlx_ptr:
        sys.stderr.write("Error: Failed to initialize MLX.\n")
        return

    win_ptr = mlx_app.mlx_new_window(
        mlx_ptr, win_width, win_height, "A-Maze-ing")

    # State Management for Interactions
    state: GameState = {
        "show_path": True,
        "color_theme_idx": 0,
        "wall_colors": [0xFF00FF00, 0xFF00FFFF, 0xFFFF00FF],  # Opaques
        "bg_color": 0xFF000000,
        "path_color": 0xFFFFD700,         # Gold path
        "entry_color": 0xFF00FF00,
        "exit_color": 0xFFFF0000,
        "pattern_colors": [0xFF8822CC, 0xFFAA44EE, 0xFFCC88FF, 0xFFAA44EE],
        # Purple pattern 42
        "drawn": False,
        "frame_count": 0,
        "path_progress": 0,
        "solution": maze.solve()
    }

    def draw_h_line(x: int, y: int, length: int, color: int) -> None:
        for i in range(length):
            mlx_app.mlx_pixel_put(mlx_ptr, win_ptr, x + i, y, color)

    def draw_v_line(x: int, y: int, length: int, color: int) -> None:
        for i in range(length):
            mlx_app.mlx_pixel_put(mlx_ptr, win_ptr, x, y + i, color)

    def draw_rect(x: int, y: int, width: int, height: int, color: int) -> None:
        for i in range(height):
            draw_h_line(x, y + i, width, color)

    def draw_static() -> None:

        mlx_app.mlx_clear_window(mlx_ptr, win_ptr)
        current_wall_color = state["wall_colors"][state["color_theme_idx"]]

        # UI
        ui_x = (maze.width * cell_size) + 20
        text_color = 0xFFFFFF
        mlx_app.mlx_string_put(mlx_ptr, win_ptr, ui_x, 40,
                               text_color, "    === MENU ===")
        mlx_app.mlx_string_put(mlx_ptr, win_ptr, ui_x, 80,
                               text_color, "Space  : New maze")
        mlx_app.mlx_string_put(mlx_ptr, win_ptr, ui_x, 105,
                               text_color, "P      : Display")
        mlx_app.mlx_string_put(mlx_ptr, win_ptr, ui_x, 125,
                               text_color, "         Hide path")
        mlx_app.mlx_string_put(mlx_ptr, win_ptr, ui_x, 150,
                               text_color, "C      : Change colors")
        mlx_app.mlx_string_put(mlx_ptr, win_ptr, ui_x, 175,
                               text_color, "Q/Esc  : Quit")

        # Wall
        for row in range(maze.height):
            for col in range(maze.width):
                cell_val = maze.maze_grid[row][col]
                px = col * cell_size
                py = row * cell_size

                if cell_val != 15:
                    if cell_val & 1:  # North
                        draw_h_line(px, py, cell_size, current_wall_color)
                    if cell_val & 2:  # East
                        draw_v_line(px + cell_size - 1, py,
                                    cell_size, current_wall_color)
                    if cell_val & 4:  # South
                        draw_h_line(px, py + cell_size - 1,
                                    cell_size, current_wall_color)
                    if cell_val & 8:  # West
                        draw_v_line(px, py, cell_size, current_wall_color)

        # Entry / Exit
        ey, ex = maze.entry
        draw_rect(ex * cell_size + 2, ey * cell_size + 2, cell_size - 4,
                  cell_size - 4, state["entry_color"])

        xy, xx = maze.exit
        draw_rect(xx * cell_size + 2, xy * cell_size + 2, cell_size - 4,
                  cell_size - 4, state["exit_color"])

    def draw_dynamic() -> None:
        # Animate Pattern
        twinkle_idx = (state["frame_count"] // 8) % len(
            state["pattern_colors"])
        current_pattern_color = state["pattern_colors"][twinkle_idx]

        for row in range(maze.height):
            for col in range(maze.width):
                if maze.maze_grid[row][col] == 15:
                    px = col * cell_size
                    py = row * cell_size
                    draw_rect(px, py, cell_size,
                              cell_size, current_pattern_color)

        # Animate Path
        solution_path = state["solution"]
        if state["show_path"] and solution_path:
            path_coords = []
            curr_y, curr_x = maze.entry

            if isinstance(solution_path, str):
                moves = {'N': (-1, 0), 'S': (1, 0), 'E': (0, 1), 'W': (0, -1)}
                for move in solution_path:
                    dy, dx = moves[move]
                    curr_y += dy
                    curr_x += dx
                    path_coords.append((curr_x, curr_y))
            else:
                path_coords = [(px, py) for (py, px) in solution_path]

            if state["frame_count"] % 1 == 0:
                state["path_progress"] += 1

            limite = min(state["path_progress"], len(path_coords))
            path_animate = path_coords[:limite]

            for px, py in path_animate:
                if (py, px) not in (maze.entry, maze.exit):
                    draw_rect(px * cell_size + 6, py * cell_size + 6,
                              cell_size - 12,
                              cell_size - 12, state["path_color"])

        mlx_app.mlx_do_sync(mlx_ptr)

    def key_hook(keycode: int, param: GameState) -> int:
        if keycode in (53, 65307, 113):  # Esc or 'q'
            mlx_app.mlx_destroy_window(mlx_ptr, win_ptr)
            mlx_app.mlx_release(mlx_ptr)
            mlx_app.mlx_loop_exit(mlx_ptr)

        elif keycode in (32, 49):  # Space
            state["path_progress"] = 0
            maze.regenerate()
            state["solution"] = maze.solve()
            state["drawn"] = False

        elif keycode in (112, 35):  # 'p'
            state["show_path"] = not state["show_path"]
            state["path_progress"] = 0
            state["solution"] = maze.solve()
            state["drawn"] = False

        elif keycode in (99, 8):  # 'c'
            state["color_theme_idx"] = (
                state["color_theme_idx"] + 1) % len(state["wall_colors"])
            state["drawn"] = False

        return 0

    def render_loop_hook(param: GameState) -> int:
        state["frame_count"] += 1
        if not state["drawn"]:
            draw_static()
            state["drawn"] = True
        draw_dynamic()

        return 0

    mlx_app.mlx_key_hook(win_ptr, key_hook, None)
    mlx_app.mlx_loop_hook(mlx_ptr, render_loop_hook, None)
    mlx_app.mlx_loop(mlx_ptr)
