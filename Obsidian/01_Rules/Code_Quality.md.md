# 📏 Code Standards and Quality

## 🐍 Environment and Standards
- [x] **Version:** The project must be written in Python 3.10 or later.
- [x] **Standard:** The project must adhere to the `flake8` coding standard.
- [x] **Main File:** The main program file must be named `a_maze_ing.py`.
- [ ] **Isolation:** It is recommended to use virtual environments for dependency isolation during development. We will use `venv`.
- [ ] **Git:** Include a `.gitignore` file to exclude Python (e.g. pycache, mypy_cache...).

## 🛡️ Robustness (Zero Crashes)
- [ ] **Error Handling:** Functions should handle exceptions gracefully to avoid crashes using `try-except` blocks. <span style="color: red;">*Note: If the program crashes due to unhandled exceptions during the review, it will be considered non-functional.</span>
- [ ] Ensure **ALL** error messages are printed to the Standard Error channel (`stderr`) using `sys.stderr.write("Error...")` and that the program exits cleanly with `sys.exit(1)`.
- [ ] **Resource Management:** All resources (e.g., file handles, network connections) must be properly managed to prevent leaks. Prefer context managers for resources like files to ensure automatic cleanup.

## 🏷️ Typing and Documentation
- [ ] **Type Hints:** The code must include type hints for function parameters, return types, and variables where applicable (using the `typing` module). 
- [ ] **Mypy Validation:** Use `mypy` for static type checking; all functions must pass without errors.
- [ ] **Docstrings:** Include docstrings in functions and classes following PEP 257 (e.g., Google or NumPy style) to document purpose, parameters, and returns.