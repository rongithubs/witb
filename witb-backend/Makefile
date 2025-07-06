# Development commands for witb-backend following CLAUDE.md

.PHONY: install format lint typecheck test test-unit test-integration run clean

install:
	pip install -r requirements-dev.txt

format:
	black .

format-check:
	black --check .

lint:
	ruff check .

typecheck:
	mypy .

test:
	pytest

test-unit:
	pytest tests/unit/

test-integration:
	pytest tests/integration/

test-cov:
	pytest --cov=. --cov-report=html

run:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

check-all: format-check lint typecheck test
	@echo "All checks passed!"