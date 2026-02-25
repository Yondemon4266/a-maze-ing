# 🛠️ Makefile Specifications

We must include a `Makefile` in our project to automate common tasks. 

## Mandatory Rules to Implement
- [x] `install`: Install project dependencies. We will use `uv` as package manager because it become the industry standard for Python development.
- [x] `run`: Execute the main script of the project (e.g., via Python interpreter).
- [x] `debug`: Run the main script in debug mode using Python's built-in debugger (e.g., pdb).
- [ ] `clean`: Remove temporary files or caches (e.g., pycache, mypy_cache) to keep the project environment clean.
- [x] `lint`: Execute the commands `flake8` and `mypy` with specific flags.
- [x] `lint-strict` *(Optional)*: Execute the commands `flake8` and `mypy --strict`.

## 📝 Required Flags for the `lint` Rule
The `mypy` command within the `lint` rule must explicitly include:
- `--warn-return-any`
- `--warn-unused-ignores`
- `--ignore-missing-imports`
- `--disallow-untyped-defs`
- `--check-untyped-defs`


## 🧠 Technical Breakdown

#### 1. Default Behavior
* The first rule `all` points to `install`. This ensures that anyone running the project for the first time starts with a clean, updated environment. 

#### 2. Efficiency (Preventing Unnecessary Work)
* **Source File:** `pyproject.toml` contains our requirements (like `flake8`, `mypy`, and `minilibx`).
* **Target/Witness File:** `.venv/uv.lock` is created by `uv` once the installation is successful. 
* **Logic:** `make` compares the timestamps of these two files.
	-  If the configuration hasn't changed, `make` skips the `uv sync` command. 
	- This mimics the behavior of not "relinking" or "recompiling".

#### 3. Project Constraints Alignment
* **Graceful Handling:** This setup ensures dependencies are installed correctly before running the main script, reducing the risk of crashes due to missing modules. 
* **Automation:** The `install` rule satisfies the mandatory requirement to automate dependency installation via a package manager of choice (uv).