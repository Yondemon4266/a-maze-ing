# 📄 Output File Structure

The generated maze must be saved to the file specified by the `OUTPUT_FILE` key in the configuration. The file must strictly follow this structural layout.

## 📝 Layout Rules
- [ ] **Grid Representation:** Cells are stored row by row, with one row per line.
- [ ] **Separator:** After the maze grid is fully printed, there must be exactly one empty line.
- [ ] **Footer Elements:** Following the empty line, these 3 elements must be inserted on 3 separate lines:
    1. The entry coordinates (e.g., `1,1`).
    2. The exit coordinates (e.g., `19,14`).
    3. The shortest valid path from entry to exit, represented by a continuous string of the letters `N`, `E`, `S`, `W`.
- [ ] **Line Endings:** All lines in the file must end with a newline character (`\n`).

## 🧪 Validation
- [ ] A validation script is provided with the subject to check that the output file contains coherent data.
- [ ] The output file might be tested automatically by a Moulinette in conjunction with its specific configuration file.