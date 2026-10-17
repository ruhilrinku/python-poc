# Employee Management API — common tasks
# On Windows, install make (e.g. `choco install make`) or run the underlying
# commands directly. Activate the venv first: .\.venv\Scripts\Activate.ps1

.DEFAULT_GOAL := help

PYTHON ?= python
PIP ?= pip
UVICORN_HOST ?= 0.0.0.0
UVICORN_PORT ?= 8000

.PHONY: help venv install env run test test-cov lint db-up db-down db-reset migrate clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

venv: ## Create the virtual environment
	$(PYTHON) -m venv .venv

install: ## Install dependencies
	$(PIP) install -r requirements.txt

env: ## Create .env from the example
	cp .env.example .env

run: ## Run the API with autoreload
	uvicorn app.main:app --reload --host $(UVICORN_HOST) --port $(UVICORN_PORT)

test: ## Run the test suite
	pytest

test-cov: ## Run tests with an HTML coverage report
	pytest --cov=app --cov-report=html --cov-report=term-missing

db-up: ## Start PostgreSQL via docker compose
	docker compose up -d

db-down: ## Stop PostgreSQL (keeps data volume)
	docker compose down

db-reset: ## Stop PostgreSQL and delete its data volume
	docker compose down -v

migrate: ## Apply Liquibase changelogs (requires Java on PATH)
	$(PYTHON) -m app.infrastructure.migrations

clean: ## Remove caches and coverage artifacts
	rm -rf .pytest_cache htmlcov .coverage
