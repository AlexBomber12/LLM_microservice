.PHONY: lint test ci

lint:
	ruff check src tests
	black --check src tests
	mypy src

test:
	pytest -m "not integration"

ci: lint test
	pytest
