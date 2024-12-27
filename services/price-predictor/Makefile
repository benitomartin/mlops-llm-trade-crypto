# Makefile

.PHONY: req training clean ruff help

req: ## Install requirements
	uv pip install -r pyproject.toml --all-extras
	uv lock

training: ## Run training
	uv run python training.py

ruff: ## Run Ruff linter
	ruff check . --fix --exit-non-zero-on-fix --show-fixes

clean: ## Clean up generated files
	rm -rf __pycache__
	rm -rf .ruff_cache

help: ## Display this help message
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
