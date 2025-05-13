.PHONY: test build clean typecheck lint format

test:
	uv run pytest

build:
	uv run pyinstaller --onefile --name shelf ./src/main.py

clean:
	rm -rf build/ __pycache__/ *.spec
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find dist/ -type f ! -name "shelf" -delete 

typecheck:
	uvx ty check

lint:
	uvx ruff check .

format:
	uvx ruff format . 