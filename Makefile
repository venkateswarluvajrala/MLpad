
.PHONY: start

start:
	PYTHONPATH=./src uv run -- kopf run -m mlpad.notebook_handler -n mlpad