# Define targets
.PHONY: install test

# Define variables
PYTHON := python


# Default target
default: install test

# Target to install package
install:
	uv pip install -e .

# Target to run tests
test:
	pytest tests/* -xv 
# $(PYTHON) -m unittest discover -s tests -p 'test_*.py' -f -v

