# Makefile

.PHONY: help clean ruff hooks

hooks: ## Run pre-commit hooks
	@echo "Running pre-commit hooks..."
	pre-commit run --all-files
	@echo "Pre-commit hooks complete."

ruff: ## Run Ruff linter 
	@echo "Running Ruff linter..."
	ruff check . --fix --exit-non-zero-on-fix --show-fixes
	@echo "Ruff linter complete."

clean: ## Clean up generated files
	@echo "Cleaning up generated files..."
	find . -type d \( -name "__pycache__" -o -name ".ruff_cache" \) -print -exec rm -rf {} +
	@echo "Cleanup complete."
	
help: ## Display this help message
	@echo "Default target: $(.DEFAULT_GOAL)"
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

