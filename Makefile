.PHONY: install run debug clean lint lint-strict

PYTHON := python3

MAIN := src.main

FILES := 

install:
	uv sync

run:
	uv run $(PYTHON) -m $(MAIN)

debug:
	uv run $(PYTHON) -m pdb -m $(MAIN)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache

lint:
	flake8 $(FILES)
	mypy $(FILES) . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 $(FILES)
	mypy $(FILES) --strict
