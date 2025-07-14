# Define targets
.PHONY: install test

# Define variables
PYTHON := python3
PI := $(PYTHON) -m pip


# Default target
default: install test

# Target to install package
install:
	uv pip install .

# Target to run tests
test:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -f -v

