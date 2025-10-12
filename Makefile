.PHONY: help test lint format clean install

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies using Poetry"
	@echo "  make test       - Run all tests with pytest"
	@echo "  make lint       - Run all linters (flake8, mypy, pylint)"
	@echo "  make format     - Format code with black and isort"
	@echo "  make clean      - Remove cache files and build artifacts"
	@echo "  make all        - Run format, lint, and test"

install:
	poetry install

test:
	poetry run pytest -v

lint: lint-flake8 lint-mypy lint-pylint

lint-flake8:
	@echo "Running flake8..."
	poetry run flake8 salary_compare tests

lint-mypy:
	@echo "Running mypy..."
	poetry run mypy salary_compare

lint-pylint:
	@echo "Running pylint..."
	poetry run pylint salary_compare

format:
	@echo "Running black..."
	poetry run black salary_compare tests
	@echo "Running isort..."
	poetry run isort salary_compare tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage
	rm -rf htmlcov/

all: format lint test
	@echo "All checks passed!"

