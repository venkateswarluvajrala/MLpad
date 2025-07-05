
.PHONY: start lint test

start:
	PYTHONPATH=. uv run -- kopf run -m src.main.mlpad.notebook.handler -n mlpad

lint:
	uv run ruff format && uv run ruff check

test:
	uv run pytest -v