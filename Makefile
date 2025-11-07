.PHONY: help install test test-unit test-integration test-pipeline coverage lint format clean

help:
	@echo "Digital Social Score - Test Commands"
	@echo "===================================="
	@echo ""
	@echo "Installation:"
	@echo "  make install           - Install dependencies"
	@echo "  make install-test      - Install test dependencies"
	@echo "  make install-all       - Install all dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test              - Run all tests"
	@echo "  make test-unit         - Run unit tests only"
	@echo "  make test-integration  - Run integration tests only"
	@echo "  make test-pipeline     - Run pipeline tests only"
	@echo "  make test-ml           - Run ML tests only"
	@echo "  make test-smoke        - Run smoke tests (quick validation)"
	@echo "  make test-watch        - Run tests in watch mode"
	@echo ""
	@echo "Coverage:"
	@echo "  make coverage          - Run tests with coverage report"
	@echo "  make coverage-html     - Generate HTML coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint              - Run linters (flake8, pylint)"
	@echo "  make type-check        - Run type checking (mypy)"
	@echo "  make format            - Auto-format code (black, isort)"
	@echo "  make security          - Run security check (bandit)"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean             - Remove build artifacts"
	@echo "  make docs              - Generate test documentation"
	@echo ""

# ============================================================================
# Installation
# ============================================================================

install:
	pip install -r requirements.txt

install-test:
	pip install -r requirements-test.txt

install-all: install install-test
	@echo "All dependencies installed!"

# ============================================================================
# Testing
# ============================================================================

test:
	pytest tests/ -v --tb=short

test-unit:
	pytest tests/unit/ -v -m unit

test-integration:
	pytest tests/integration/ -v -m integration

test-pipeline:
	pytest tests/pipeline/ -v -m pipeline

test-ml:
	pytest tests/ml/ -v -m ml

test-api:
	pytest tests/integration/test_api_endpoints.py -v -m api

test-smoke:
	pytest tests/ -v -m smoke --timeout=60

test-watch:
	pytest-watch tests/ -- -v --tb=short

# ============================================================================
# Coverage
# ============================================================================

coverage:
	pytest tests/ --cov=src --cov-report=term-missing --cov-report=html -v

coverage-html: coverage
	@echo "Coverage report generated in htmlcov/index.html"

coverage-report:
	coverage report -m
	coverage html

# ============================================================================
# Code Quality
# ============================================================================

lint:
	flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
	pylint src/ tests/ --disable=all --enable=E,F 2>/dev/null || true

lint-strict:
	flake8 src/ tests/ --max-line-length=100
	pylint src/ tests/ --fail-under=8.0

format:
	black src/ tests/
	isort src/ tests/

format-check:
	black src/ tests/ --check
	isort src/ tests/ --check-only

type-check:
	mypy src/ --ignore-missing-imports --strict

security:
	bandit -r src/ -v

# ============================================================================
# Build and Clean
# ============================================================================

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .eggs/ *.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .coverage htmlcov/
	rm -rf tests/logs/

# ============================================================================
# Documentation
# ============================================================================

docs:
	pytest tests/ --html=reports/test_report.html --self-contained-html
	@echo "Test report generated in reports/test_report.html"

# ============================================================================
# CI/CD Simulation
# ============================================================================

ci: clean lint type-check coverage
	@echo "CI pipeline completed successfully!"

pre-commit: format lint test-unit
	@echo "Pre-commit checks passed!"
