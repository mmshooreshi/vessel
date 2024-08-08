# Directory variables
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
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv $(VENV_DIR); \
		echo "Virtual environment created."; \
	else \
		echo "Virtual environment already exists."; \
	fi

# Install dependencies
.PHONY: install-deps
install-deps: venv
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip setuptools wheel
	@if [ -f requirements.txt ]; then \
		$(PIP) install -r requirements.txt; \
	else \
		echo "No requirements.txt found, skipping installation."; \
	fi

# Generate requirements.txt using pipreqs
.PHONY: gen-reqs
gen-reqs: venv
	@echo "Generating requirements.txt..."
	$(PIP) install pipreqs
	$(PIPREQS) . --force
	@echo "requirements.txt generated."

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
	@if [ -f requirements.txt ]; then \
		rm -f requirements.txt; \
	fi
	@echo "Clean up completed."

# Remove only .pyc files and __pycache__ directories
.PHONY: clean-pyc
clean-pyc:
	@echo "Removing .pyc files and __pycache__ directories..."
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	@echo "Removed .pyc files and __pycache__ directories."

# Run tests (if you have a test script)
.PHONY: test
test: install-deps
	@echo "Running tests..."
	$(PYTHON) -m unittest discover tests

# Update pipreqs and regenerate requirements.txt
.PHONY: update-reqs
update-reqs: venv
	@echo "Updating pipreqs and regenerating requirements.txt..."
	$(PIP) install --upgrade pipreqs
	$(PIPREQS) . --force
	@echo "requirements.txt updated."

# Check for outdated dependencies
.PHONY: check-updates
check-updates: venv
	@echo "Checking for outdated dependencies..."
	$(PIP) list --outdated

# Upgrade all dependencies to the latest versions
.PHONY: upgrade-deps
upgrade-deps: venv
	@echo "Upgrading all dependencies to the latest versions..."
	$(PIP) install --upgrade pip
	$(PIP) list --outdated | awk 'NR>2 {print $$1}' | xargs -n1 $(PIP) install --upgrade
	@echo "All dependencies upgraded."

# Freeze current dependencies to requirements.txt
.PHONY: freeze-reqs
freeze-reqs: venv
	@echo "Freezing current dependencies to requirements.txt..."
	$(PIP) freeze > requirements.txt
	@echo "Dependencies frozen to requirements.txt."

# Check Python code formatting with black
.PHONY: format-check
format-check: venv
	@echo "Checking Python code formatting with black..."
	$(PIP) install black
	$(VENV_DIR)/bin/black --check .

# Format Python code with black
.PHONY: format
format: venv
	@echo "Formatting Python code with black..."
	$(PIP) install black
	$(VENV_DIR)/bin/black .
	@echo "Python code formatted."

# Lint Python code with flake8
.PHONY: lint
lint: venv
	@echo "Linting Python code with flake8..."
	$(PIP) install flake8
	$(VENV_DIR)/bin/flake8 .

# Run the main script in production mode
.PHONY: prod
prod: install-deps
	@echo "Running the main script in production mode..."
	ENV=production $(PYTHON) vessel.py
