PYTHON = uv run python3 
MAIN = a_maze_ing.py
CONFIG = config.txt
SRC = $(MAIN) mazegen/

all: install

install: .venv/uv.lock
.venv/uv.lock: pyproject.toml
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
	uv build
	@echo "Moving the package to the root of the repository..."
	mv dist/mazegen-* ./
	rm -rf dist/

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__ \
	rm -rf mazegen/__pycache__ \
	.mypy_cache \
	.venv dist/ \
	mazegen-*.whl \
	mazegen-*.tar.gz \
	mazegen.egg-info* \
	uv.lock

.PHONY: install run debug lint lint-strict build clean
