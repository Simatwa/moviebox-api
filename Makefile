# Define targets
.PHONY: install test coverage-badge

# Define variables
PYTHON := python


# Default target
default: install test

# Target to install package
install:
	uv pip install -e ".[cli]"

# Target to install in termux
install-in-termux:
	pip install moviebox-api --no-deps
	pip install 'pydantic==2.9.2'
	pip install rich click bs4 httpx throttlebuster

# Target to run tests
test:
	coverage run -m pytest -v

# Target to generate coverage-badge
coverage-badge:
	coverage-badge -o assets/coverage.svg -f

# target to build dist
build:
	rm build/ dist/ -rf
	uv build
	
# Target to publish dist to pypi
publish:
	uv publish --token $(shell get pypi)


