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

.PHONY: help venv install clean run test docker-up docker-down clean install-test

help: ## Display this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-30s$(NC) %s\n", $$1, $$2}'

install: ## Install dependencies
	@echo "Installing dependencies..."
	@$(PYTHON) -m pip install --upgrade pip setuptools wheel
	@$(PYTHON) -m pip install -r $(REQUIREMENTS)
	@echo "Dependencies installed successfully"

install-test: ## Install test dependencies
	@echo "Installing test dependencies..."
	@$(PIP) install -e ".[test]"
	@echo "Test dependencies installed successfully"

run: ## Run the application
	@echo "Starting TF Code Analyzer Agent..."
	@$(PYTHON) app/main.py

ifeq ($(OS),Windows_NT)
test: install-test ## Run tests
	@echo "Running tests..."
	@set PYTHONPATH=%CD% && pytest tests/ -v
else
test: install-test ## Run tests
	@echo "Running tests..."
	@PYTHONPATH=$(shell pwd) pytest tests/ -v
endif

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
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .coverage
	rm -rf htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete

# Default target
.DEFAULT_GOAL := help