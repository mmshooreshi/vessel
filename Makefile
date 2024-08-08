# Define variables
VENV_DIR := venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip
PIPREQS := $(VENV_DIR)/bin/pipreqs

# Load environment variables from .env
include .env
export $(shell sed 's/=.*//' .env)

# Define colors
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
PURPLE=\033[0;35m
CYAN=\033[0;36m
GRAY=\033[1;30m
NC=\033[0m # No Color

# Define a function to show spinner
spinner = /bin/bash -c 'spin() { \
    spinner="/|\\-/"; \
    while kill -0 $$1 2>/dev/null; do \
        for i in `seq 0 3`; do \
            echo -ne "\r${CYAN}[...]${NC} $2 ${spinner:$i:1}"; \
            sleep 0.1; \
        done; \
    done; \
    echo -ne "\r${GREEN}✔${NC} $2 Completed\n"; \
}; \
spin $$! "$1" "$2" & \
wait $$1'

# Default target
.PHONY: all
all: venv install-deps run

# Create virtual environment
.PHONY: venv
venv:
	@echo -e "${CYAN}====================================================${NC}"
	@echo -e "${CYAN}● Creating virtual environment in $(VENV_DIR)...${NC}"
	@$(call spinner,$(shell python3 -m venv $(VENV_DIR) & echo $$!),"Creating virtual environment")
	@echo -e "${GREEN}✔ Virtual environment created successfully.${NC}"
	@echo -e "${CYAN}====================================================${NC}"

# Install dependencies
.PHONY: install-deps
install-deps: venv
	@echo -e "${CYAN}====================================================${NC}"
	@echo -e "${CYAN}● Installing PySocks for SOCKS proxy support...${NC}"
	@$(call spinner,$(shell $(PIP) install -i https://mirror-pypi.runflare.com/simple pysocks & echo $$!),"Installing PySocks")
	@echo -e "${GREEN}✔ PySocks installed successfully.${NC}"
	@echo -e "${CYAN}----------------------------------------------------${NC}"
	@echo -e "${CYAN}● Installing dependencies from requirements.txt using SOCKS proxy...${NC}"
	@$(call spinner,$(shell $(PIP) install -i https://mirror-pypi.runflare.com/simple -r requirements.txt & echo $$!),"Installing dependencies")
	@echo -e "${GREEN}✔ Dependencies installed successfully.${NC}"
	@echo -e "${CYAN}====================================================${NC}"

# Generate requirements.txt using pipreqs
.PHONY: gen-reqs
gen-reqs: venv
	@echo -e "${CYAN}====================================================${NC}"
	@echo -e "${CYAN}● Generating requirements.txt using pipreqs...${NC}"
	@$(call spinner,$(shell $(PIP) install -i https://mirror-pypi.runflare.com/simple pipreqs & echo $$!),"Installing pipreqs")
	@$(call spinner,$(shell $(PIPREQS) . & echo $$!),"Generating requirements.txt")
	@echo -e "${GREEN}✔ requirements.txt generated successfully.${NC}"
	@echo -e "${CYAN}====================================================${NC}"

# Run the main Python script
.PHONY: run
run: install-deps
	@echo -e "${CYAN}====================================================${NC}"
	@echo -e "${CYAN}● Running the main script (vessel.py)...${NC}"
	@$(call spinner,$(shell $(PYTHON) vessel.py & echo $$!),"Running script")
	@echo -e "${GREEN}✔ Script execution completed.${NC}"
	@echo -e "${CYAN}====================================================${NC}"

# Clean up the environment (remove venv and .pyc files)
.PHONY: clean
clean:
	@echo -e "${CYAN}====================================================${NC}"
	@echo -e "${CYAN}● Cleaning up the environment...${NC}"
	@$(call spinner,$(shell rm -rf $(VENV_DIR) & find . -name '*.pyc' -delete & find . -name '__pycache__' -delete & rm -f requirements.txt & echo $$!),"Cleaning up")
	@echo -e "${GREEN}✔ Environment cleaned up successfully.${NC}"
	@echo -e "${CYAN}====================================================${NC}"

# Remove only .pyc files and __pycache__ directories
.PHONY: clean-pyc
clean-pyc:
	@echo -e "${CYAN}====================================================${NC}"
	@echo -e "${CYAN}● Removing .pyc files and __pycache__ directories...${NC}"
	@$(call spinner,$(shell find . -name '*.pyc' -delete & find . -name '__pycache__' -delete & echo $$!),"Removing .pyc files")
	@echo -e "${GREEN}✔ .pyc files and __pycache__ directories removed.${NC}"
	@echo -e "${CYAN}
