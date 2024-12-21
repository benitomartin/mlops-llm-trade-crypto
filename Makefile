# Makefile

.PHONY: help clean clean-state ruff hooks

hooks: ## Run pre-commit hooks
	@echo "Running pre-commit hooks..."
	pre-commit run --all-files
	@echo "Pre-commit hooks complete."

ruff: ## Run Ruff linter
	@echo "Running Ruff linter..."
	ruff check . --fix --exit-non-zero-on-fix --show-fixes
	@echo "Ruff linter complete."

clean: ## Clean up cached generated files
	@echo "Cleaning up generated files..."
	find . -type d \( -name "__pycache__" -o -name ".ruff_cache" -o -name ".pytest_cache" -o -name ".mypy_cache" \) -exec rm -rf {} +
	@echo "Cleanup complete."

clean-state: ## Clean state generated files
	@echo "Cleaning state generated files..."
	find . -type d -name "state" -exec rm -rf {} +
	@echo "Cleanup complete."

help: ## Display this help message
	@echo "Default target: $(.DEFAULT_GOAL)"
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
