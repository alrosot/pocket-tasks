.PHONY: install install-dev test test-emulator lint format clean run help

PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
FLAKE8 := $(PYTHON) -m flake8

# Default target
help:
	@echo "pocket-tasks Makefile commands:"
	@echo ""
	@echo "  make install        Install production dependencies"
	@echo "  make install-dev    Install development dependencies"
	@echo "  make test           Run unit tests with coverage"
	@echo "  make test-emulator  Run manual tests with luma.emulator"
	@echo "  make lint           Check code style with flake8"
	@echo "  make format         Format code with black"
	@echo "  make clean          Remove test artifacts and cache"
	@echo "  make run            Start the application"
	@echo "  make help           Show this help message"

install:
	$(PIP) install -r requirements.txt

install-dev: install
	$(PIP) install -r requirements-dev.txt

test:
	$(PYTEST) tests/ -v --cov=src --cov-report=html --cov-report=term-missing

test-emulator:
	@echo "Starting pocket-tasks with luma.emulator..."
	LUMA_EMULATOR=1 $(PYTHON) src/app.py

lint:
	$(FLAKE8) src/ tests/ --max-line-length=100 --count --statistics

format:
	$(BLACK) src/ tests/ --line-length=100

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	@echo "Cleaned up test artifacts and cache"

run:
	$(PYTHON) src/app.py
