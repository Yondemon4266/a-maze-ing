# 🧱 Maze Constraints & Validity

To be considered valid, the generated maze data must strictly follow these structural rules.

## 📏 Structural Rules
- [ ] **Wall Count:** Each cell has between 0 and 4 walls at each cardinal point (North, East, South, West).
- [ ] **Entry and Exit:** Entry and exit must exist, be different, and be inside the maze bounds. Since they are specific cells, there must be walls at the external borders.
- [ ] **Connectivity:** The structure must ensure full connectivity with no isolated cells, except for the "42" pattern.
- [ ] **Data Coherence:** Each neighboring cell must have the same wall status if any. For example, if a cell has a wall on its east side, the adjacent cell to its east MUST have a wall on its west side.
- [ ] **No Large Open Areas:** Corridors cannot be wider than 2 cells. For example, 2x3 or 3x2 open areas are allowed, but a 3x3 open area is strictly forbidden.