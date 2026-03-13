PYTHON = uv run python3 
MAIN = a_maze_ing.py
CONFIG = config.txt
SRC = .

install: .venv/uv.lock
.venv/uv.lock: pyproject.toml lib/mlx-2.2-py3-none-any.whl
	@echo "Installing dependencies using uv..."
	uv sync
	@touch .venv/uv.lock

run: install
	@echo "Running the maze generator..."
	$(PYTHON) $(MAIN) $(CONFIG) 

debug: install
	@echo "Starting debug mode..."
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

lint: install
	@echo "Running standard linting..."
	uv run flake8 $(SRC)
	uv run mypy $(SRC)

lint-strict: install
	@echo "Running strict linting..."
	uv run flake8 $(SRC)
	uv run mypy --strict $(SRC)

build: install
	@echo "Building the standalone module..."
	uv build --wheel
	@echo "Moving the package to the root of the repository..."
	mv dist/mazegen-* ./
	rm -rf dist/

clean:
	@echo "Cleaning up..."
	rm -rf .mypy_cache \
	       mazegen-*.whl \
	       mazegen-*.tar.gz \
	       src/mazegen.egg-info* \
	       dist/ \
		   build \
		   uv.lock \

	find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean
	rm -rf .venv


.PHONY: install run debug lint lint-strict build clean fclean
