# Define targets
.PHONY: install test build publish install-in-termux

# Define variables
PYTHON := python


# Default target
default: install test

# Target to install package
install:
	uv pip install -e .

# Target to install in termux
install-in-termux:
	pip install moviebox-api --no-deps
	pip install 'pydantic==2.9.2'
	pip install rich click httpx tqdm

# Target to run tests
test:
	pytest tests/* -xv 

# target to build dist
build:
	rm build/ disr/ -rf
	uv build
	
# Target to publish dist to pypi
publish:
	uv publish --token $(shell get pypi)

# $(PYTHON) -m unittest discover -s tests -p 'test_*.py' -f -v

