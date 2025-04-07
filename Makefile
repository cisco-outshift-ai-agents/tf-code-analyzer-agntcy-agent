# Makefile for TF Code Analyzer Agent

# Variables
PYTHON := python3
PIP := pip
DOCKER_COMPOSE := docker-compose

# Python settings
VENV := venv
REQUIREMENTS := requirements.txt

# Colors for terminal output
GREEN := \033[0;32m
NC := \033[0m # No Color

.PHONY: help venv install clean run test docker-up docker-down install-venv

help: ## Display this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-30s$(NC) %s\n", $$1, $$2}'

install: ## Install dependencies
	@echo "Installing dependencies..."
	@$(PIP) install -r $(REQUIREMENTS)
	@echo "Dependencies installed successfully"

run: ## Run the application
	@echo "Starting TF Code Analyzer Agent..."
	@$(PYTHON) app/main.py

test: ## Run tests
	@echo "Running tests..."
	@pytest tests/ -v

docker-up: ## Start services with docker-compose
	@echo "Starting services with docker-compose..."
	@$(DOCKER_COMPOSE) up -d --build

docker-down: ## Stop docker-compose services
	@echo "Stopping services..."
	@$(DOCKER_COMPOSE) down

# Default target
.DEFAULT_GOAL := help