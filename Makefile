# Define variables
VENV_DIR := venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip
PIPREQS := $(VENV_DIR)/bin/pipreqs

# Default target
.PHONY: all
all: venv install-deps run

# Create virtual environment
.PHONY: venv
venv:
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV_DIR)

# Install dependencies
.PHONY: install-deps
install-deps: venv
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Generate requirements.txt using pipreqs
.PHONY: gen-reqs
gen-reqs: venv
	@echo "Generating requirements.txt..."
	$(PIPREQS) .

# Run the main Python script
.PHONY: run
run: install-deps
	@echo "Running the main script..."
	$(PYTHON) vessel.py

# Clean up the environment (remove venv and .pyc files)
.PHONY: clean
clean:
	@echo "Cleaning up..."
	rm -rf $(VENV_DIR)
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	rm -f requirements.txt

# Remove only .pyc files and __pycache__ directories
.PHONY: clean-pyc
clean-pyc:
	@echo "Removing .pyc files and __pycache__ directories..."
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

# Run tests (if you have a test script)
.PHONY: test
test: install-deps
	@echo "Running tests..."
	$(PYTHON) test.py
