# ⚙️ Configuration Parsing

The program takes a single argument, `config.txt`, which defines the maze generation options. 

## 📝 Parsing Rules
- [ ] **Format:** The configuration file must contain one `KEY=VALUE` pair per line.
- [ ] **Comments:** Lines starting with `#` are comments and must be ignored.
- [ ] **Error Handling:** The program must handle all errors gracefully (invalid configuration, file not found, bad syntax, impossible parameters). It must never crash unexpectedly and must provide a clear error message.
- [ ] **Default Config:** A default configuration file must be available in the Git repository.

## 🔑 Mandatory Keys
The following keys must be implemented and parsed correctly:
* `WIDTH`: Maze width (number of cells) (e.g., `WIDTH=20`).
* `HEIGHT`: Maze height (e.g., `HEIGHT=15`).
* `ENTRY`: Entry coordinates (x,y) (e.g., `ENTRY=0,0`).
* `EXIT`: Exit coordinates (x,y) (e.g., `EXIT=19,14`).
* `OUTPUT_FILE`: Output filename (e.g., `OUTPUT_FILE=maze.txt`).
* `PERFECT`: Is the maze perfect? (e.g., `PERFECT=True`) .

*Note: We can add additional keys like seed, algorithm, or display mode if useful.*