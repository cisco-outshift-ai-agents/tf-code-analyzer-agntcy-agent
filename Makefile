# Makefile for TF Code Analyzer Agent

# Variables
PYTHON := python3
PIP := pip
DOCKER_COMPOSE := docker-compose

# Python settings
VENV := venv
VENV_DOT := .venv
REQUIREMENTS := requirements.txt

# Colors for terminal output
GREEN := \033[0;32m
NC := \033[0m # No Color

.PHONY: help venv install clean run test docker-up docker-down install-dev clean install-test

help: ## Display this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-30s$(NC) %s\n", $$1, $$2}'

install: ## Install dependencies
	@echo "Installing dependencies..."
	@$(PIP) install -r $(REQUIREMENTS)
	@echo "Dependencies installed successfully"

install-pkg-venv: ## Install package dependencies
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		echo "Using already activated virtual environment: $$VIRTUAL_ENV"; \
		$(PIP) install -r $(REQUIREMENTS)"; \
	elif [ -d "$(VENV_DOT)" ]; then \
		echo "Using existing .venv directory..."; \
		. $(VENV_DOT)/bin/activate && $(PIP) install -r $(REQUIREMENTS); \
	elif [ -d "$(VENV)" ]; then \
		echo "Using existing venv directory..."; \
		. $(VENV)/bin/activate &&  $(PIP) install -r $(REQUIREMENTS); \
	else \
		echo "Creating virtual environment..."; \
		python -m venv $(VENV); \
		. $(VENV)/bin/activate && $(PIP) install -r $(REQUIREMENTS); \
	fi

install-dev: install-pkg-venv ## Install package in development mode with test dependencies
	@echo "Development installation complete! If not already activated, activate your virtual environment with:"
	@echo "On Unix/Linux/Mac: source $(VENV)/bin/activate"
	@echo 'On Windows: $(VENV)\Scripts\activate'

install-test: ## Install test dependencies
	@echo "Installing test dependencies..."
	@$(PIP) install -e ".[test]"
	@echo "Test dependencies installed successfully"

run: ## Run the application
	@echo "Starting TF Code Analyzer Agent..."
	@$(PYTHON) app/main.py

test: install-test ## Run tests
	@echo "Running tests..."
	@PYTHONPATH=$(PWD) pytest tests/ -v

docker-up: ## Start services with docker-compose
	@echo "Starting services with docker-compose..."
	@$(DOCKER_COMPOSE) up -d --build

docker-down: ## Stop docker-compose services
	@echo "Stopping services..."
	@$(DOCKER_COMPOSE) down

clean: ## Clean up development environment
	@echo "Cleaning up..."
	rm -rf $(VENV)
	rm -rf $(VENV_DOT)
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +

# Default target
.DEFAULT_GOAL := help