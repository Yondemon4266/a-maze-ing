# 🗺️ Project "A-Maze-ing" Work Strategy

**Never push directly to `main`!** 
**Creat unitary test ** 

## 🏗️ Phase 1: Foundations
* **Tasks:** * Create `a_maze_ing.py`.
  * Set up `sys.argv` parsing to strictly accept only one `config.txt` argument.
  * Implement the global `try/except` skeleton to prevent unexpected crashes (mandatory requirement).

## ⚙️ Phase 2: Core Logic (Cross-Division)

* **Dev A (The Parser):** Reads `config.txt`, validates the data (dimensions, characters allowed), and initializes the empty grid/data structure.

* **Dev B (The Algorithm):** Writes the actual maze generation algorithm (e.g., Recursive Backtracking or Prim's). Takes the empty grid and "carves" the paths.

## 🎨 Phase 3: Graphics & MiniLibX (Specialization)

* **Dev A (The Renderer):** Writes the loop that reads the generated grid and calls MiniLibX drawing functions (pixels, squares, colors for walls vs. paths).

* **Dev B (The Controller):** Handles window creation (`mlx_new_window`), hooks/events (pressing `ESC` to quit, clicking the red cross), and ensures clean destruction to prevent memory leaks.
## 🧠 Phase 4: The Solver (Pathfinding) 

* **Dev A (The Pathfinder):** Implements the solving algorithm (like BFS for the shortest path, or A*). This function takes the generated grid, finds the start and end points, and returns the list of coordinates that form the winning route. 

* **Dev B (The Path Renderer):** Updates the graphical engine. Takes the list of winning coordinates from Dev A and draws the solution path on the screen (e.g., drawing a distinct red line or colored squares from the entrance to the exit).

## 🧹 Phase 5: Final
* ****
* **Tasks:**
  * Run `make lint` and fix all `flake8` and `mypy` strict errors together.
  * Run `make build` and test the generated `.whl` file via `pip install`.
  * Update `README.md` with instructions on how to install `uv` and run the project.