# Define variables
VENV_DIR := venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip
PIPREQS := $(VENV_DIR)/bin/pipreqs

# Load environment variables from .env
include .env
export $(shell sed 's/=.*//' .env)

# Default target
.PHONY: all
all: venv install-deps run

# Create virtual environment
.PHONY: venv
venv:
	@echo "Creating virtual environment in $(VENV_DIR)..."
	@python3 -m venv $(VENV_DIR)
	@echo "Virtual environment created successfully."

# Install dependencies
.PHONY: install-deps
install-deps: venv
	@echo "Installing PySocks for SOCKS proxy support..."
	@$(PIP) install --proxy=$(SOCKS_PROXY) pysocks
	@echo "Installing dependencies from requirements.txt using SOCKS proxy..."
	@$(PIP) install --proxy=$(SOCKS_PROXY) --upgrade pip
	@$(PIP) install --proxy=$(SOCKS_PROXY) -r requirements.txt
	@echo "Dependencies installed successfully."

# Generate requirements.txt using pipreqs
.PHONY: gen-reqs
gen-reqs: venv
	@echo "Generating requirements.txt using pipreqs..."
	@$(PIP) install pipreqs  # Ensure pipreqs is installed
	@$(PIPREQS) .
	@echo "requirements.txt generated successfully."

# Run the main Python script
.PHONY: run
run: install-deps
	@echo "Running the main script (vessel.py)..."
	@$(PYTHON) vessel.py
	@echo "Script execution completed."

# Clean up the environment (remove venv and .pyc files)
.PHONY: clean
clean:
	@echo "Cleaning up the environment..."
	@rm -rf $(VENV_DIR)
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -delete
	@rm -f requirements.txt
	@echo "Environment cleaned up successfully."

# Remove only .pyc files and __pycache__ directories
.PHONY: clean-pyc
clean-pyc:
	@echo "Removing .pyc files and __pycache__ directories..."
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -delete
	@echo ".pyc files and __pycache__ directories removed."

# Run tests (if you have a test script)
.PHONY: test
test: install-deps
	@echo "Running tests using test.py..."
	@$(PYTHON) test.py
	@echo "Tests executed successfully."
