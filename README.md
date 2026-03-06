*This project has been created as part of the 42 curriculum by advacher, aluslu.*

---

#  A-Maze-ing

A fully-featured **maze generator**, **solver**, and **interactive visualizer** written in Python.
It reads a configuration file, builds a maze using selectable algorithms, solves it via BFS, exports the result in hexadecimal format, and renders everything in a real-time MiniLibX window with animations and keyboard controls.

---

## Table of Contents

1. [Description](#-description)
2. [Instructions](#-instructions)
3. [Configuration File](#-configuration-file)
4. [Maze Generation Algorithms](#-maze-generation-algorithms)
5. [Interactive Display](#-interactive-display)
6. [Reusable Module (`mazegen`)](#-reusable-module-mazegen)
7. [Team & Project Management](#-team--project-management)
8. [Resources & AI Usage](#-resources--ai-usage)

---

## Description

**A-Maze-ing** generates customizable 2D mazes from a simple `config.txt` file.
The project is split into three pillars:

| Pillar | What it does |
|---|---|
| **Generation** | Builds the maze grid using DFS (Recursive Backtracker) or Prim's algorithm. |
| **Solving** | Finds the shortest path from entry to exit using BFS. |
| **Visualization** | Renders the maze in a fullscreen MiniLibX window with animated path tracing, pattern "42" twinkle, and live keyboard interaction. |

The maze data is encoded in a **4-bit bitmask** per cell (`1`=North, `2`=East, `4`=South, `8`=West) and exported as hexadecimal characters to an output file.

---

## Instructions

### Prerequisites

- **Python** ≥ 3.10
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager (used by the Makefile)

### Makefile Rules

| Command | Description |
|---|---|
| `make install` | Installs all project dependencies via `uv sync`. |
| `make run` | Generates, solves, exports, and displays the maze. |
| `make debug` | Runs the script through `pdb` for debugging. |
| `make lint` | Runs `flake8` and `mypy` checks. |
| `make lint-strict` | Runs `flake8` and `mypy --strict`. |
| `make build` | Builds the `mazegen` package (`.whl`) and places it at the repo root. |
| `make clean` | Removes caches, build artifacts, and `__pycache__` directories. |
| `make fclean` | `clean` + removes the `.venv` virtual environment. |

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Yondemon4266/a-maze-ing.git
cd a-maze-ing

# 2. Install dependencies & run
make run
```

---

## Configuration File

The maze is configured through a plain-text file (`config.txt`) using `KEY=VALUE` pairs.
Lines starting with `#` are treated as comments and ignored.

### Keys

| Key | Type | Required | Description |
|---|---|---|---|
| `WIDTH` | `int` | ✅ | Number of cells horizontally. |
| `HEIGHT` | `int` | ✅ | Number of cells vertically. |
| `ENTRY` | `x,y` | ✅ | Entry point coordinates (must be on a border). |
| `EXIT` | `x,y` | ✅ | Exit point coordinates (must be on a border). |
| `OUTPUT_FILE` | `str` | ✅ | Path to the output file for the hex-encoded maze. |
| `PERFECT` | `bool` | ✅ | `TRUE` for a perfect maze (single unique path), `FALSE` otherwise. |
| `ALGORITHM` | `str` | OPTIONAL | Generation algorithm: `DFS` or `PRIM`. |
| `SEED` | `int` | OPTIONAL | Reproducible generation — same seed = same maze. |

### Example

```ini
# Maze dimensions
WIDTH=40
HEIGHT=20

# Entry and exit on the border
ENTRY=0,0
EXIT=39,19

# Output
OUTPUT_FILE=output_maze.txt

# Generation settings
PERFECT=TRUE
ALGORITHM=DFS
SEED=42
```

---

##  Maze Generation Algorithms

### DFS — Recursive Backtracker

A randomized depth-first search that **carves** passages by visiting unvisited neighbours and backtracking when stuck.

- ✅ Guarantees a **perfect maze** (exactly one path between any two cells).
- Creates long, winding corridors — challenging to solve.
- Efficient: O(W × H) time complexity.

**Why we chose it →** It is the gold standard for perfect maze generation: fast, elegant, and produces aesthetically pleasing labyrinths.

### Prim's Algorithm

Starts from a random cell and repeatedly adds the **lowest-cost frontier** wall, growing the maze outward.

- Produces shorter dead-ends and a more "organic" branching structure.
- Good variety compared to DFS.

**Why we chose it →** Provides a visual contrast to DFS. The sprawling, tree-like structure feels more natural and gives users a meaningful choice between algorithms.

### BFS — Solver

Breadth-first search explores all directions **layer by layer**, guaranteeing the **shortest path** in an unweighted grid.

**Why we chose it →** Unlike DFS which finds *a* path, BFS finds *the* optimal path — critical for displaying a meaningful solution to the user.

---

## Interactive Display

The maze is rendered in a fullscreen **MiniLibX** window with real-time animations.

### Keyboard Controls

| Key | Action |
|---|---|
| `Space` | Regenerate a new maze and restart the path animation. |
| `P` | Toggle the solution path display on / off. |
| `C` | Cycle through wall color themes (green → cyan → magenta). |
| `Q` / `Esc` | Quit the application. |

### Visual Features

- **Animated path tracing** — the solution draws itself cell by cell from entry to exit.
- **"42" pattern twinkle** — if the maze is large enough to embed the "42" pattern, the pattern cells pulse with a color animation.
- **Wall color themes** — three distinct color themes, switchable in real time.
- **Entry / Exit markers** — green square for entry, red square for exit.
- **Centered layout** — the maze is always centered on screen with a key-bindings menu displayed below.

---

##  Reusable Module (`mazegen`)

The maze generation logic is packaged as a **standalone, pip-installable Python module** called `mazegen`.

### Building the Package

```bash
# From the repo root, in a virtualenv:
make build
# → produces: mazegen-1.0.0-py3-none-any.whl at the repo root
```

### Installing the Package

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Usage in Your Own Project

```python
from mazegen import MazeGenerator

# Instantiate with a config file — generation is automatic
maze = MazeGenerator("config.txt")

# Access the 2D grid (bitmask walls: 1=N, 2=E, 4=S, 8=W)
grid: list[list[int]] = maze.maze_grid

# Solve and get a direction string (e.g. "SSENESS...")
path: str | None = maze.solve()

# Regenerate with same config
maze.regenerate()
```

### What's Inside

| Component | Description |
|---|---|
| `MazeGenerator` | Main class — generates and solves the maze. |
| `MazeConfig` | Pydantic model for validated configuration. |
| `MazeConfigParser` | Parses `KEY=VALUE` config files with error handling. |
| `MazeConfigParserError` | Custom exception for config parsing failures. |

>  Full package documentation is available in [`src/mazegen/README.md`](src/mazegen/README.md).

---

##  Team & Project Management

### Team

| Member | Login | Role |
|---|---|---|
| **Dev A** | `aluslu` | Parser, Renderer, Path Renderer |
| **Dev B** | `advacher` | Algorithm Engineer, Controller, Pathfinder |

### Roles by Phase

| Phase | Dev A (`aluslu`) | Dev B (`advacher`) |
|---|---|---|
| **Phase 1 — Core Logic** | Config parser: reads `config.txt`, validates data with Pydantic, and Prim algorithm. | Maze generation algorithms: implements DFS Recursive Backtracker. |
| **Phase 2 — Graphics** | MiniLibX renderer: image buffer management, pixel drawing, wall rendering, color themes. | Window controller: MiniLibX window creation, event hooks (keyboard, close), clean resource destruction. |
| **Phase 3 — Solver** | Path renderer: animates the BFS solution on screen with progressive drawing. | BFS pathfinder: implements the solver, returns the optimal direction string. |

### Planning & Evolution

| Week | Planned | Actual |
|---|---|---|
| **Week 1** | Config parsing + DFS generation | ✅ Completed on schedule. Added Pydantic validation. |
| **Week 2** | Hex output + basic MiniLibX display | ✅ Output file works. MiniLibX rendering functional but with flickering issues. Solver + path display + polish ✅ BFS solver done. Resolved flicker with split-image approach. Added animations, color themes, and interactive controls. Packaging + README + cleanup | ✅ `mazegen` module packaged. README finalized. Linting passed. |

### What Worked Well

- **PR-based Git workflow** — every feature on a dedicated branch, line-by-line code reviews before merge. No direct pushes to `main`.
- **Clear role separation** — Parser vs Algorithm split avoided merge conflicts and allowed parallel development.
- **Iterative rendering** — progressive approach to fixing MiniLibX flicker led to a clean cache-based architecture.

### What Could Be Improved

- **Earlier MiniLibX prototyping** — we underestimated the flicker problem; starting display work sooner would have saved time.
- **Automated testing** — unit tests for the generator module would have caught edge cases faster.

### Tools Used

| Tool | Purpose |
|---|---|
| **uv** | Fast Python package management and virtual environment. |
| **Git + GitHub** | Version control with branch-based PR workflow. |
| **flake8 + mypy** | Linting and static type checking. |
| **MiniLibX (Python)** | Graphics rendering library (42 school standard). |
| **Pydantic** | Configuration validation and data modeling. |
| **VS Code** | Primary development environment. |

---

## Resources & AI Usage

### References

| Resource | Link |
|---|---|
| MiniLibX Documentation | [harm-smits.github.io/42docs/libs/minilibx](https://harm-smits.github.io/42docs/libs/minilibx) |
| DFS & BFS Algorithms (Video) | [youtube.com/watch?v=cS-198wtfj0](https://www.youtube.com/watch?v=cS-198wtfj0) |
| Python Packaging Guide | [packaging.python.org](https://packaging.python.org/) |
| Pydantic Documentation | [docs.pydantic.dev](https://docs.pydantic.dev/) |

### AI Usage

AI (GitHub Copilot) was used as a **development assistant** for the following tasks:

| Task | How AI helped |
|---|---|
| **MiniLibX Python adaptation** | Translated low-level C paradigms (`mlx_pixel_put`, image buffers) into efficient Pythonic structures with bulk writes. |
| **Rendering optimization** | Identified the flicker root cause (image overwriting text) and guided the split-image / static-cache architecture. |
| **Algorithmic edge cases** | Helped refine DFS backtracking logic and BFS queue management for large mazes. |
| **Bitmask encoding** | Validated the 4-bit wall encoding system to ensure data integrity between generator and output file. |
| **Documentation** | Assisted in structuring this README to meet project requirements. |

> AI was **not** used to generate the core algorithms from scratch — all generation, solving, and rendering logic was written and understood by the team. AI served as an accelerator for debugging, optimization, and documentation.
