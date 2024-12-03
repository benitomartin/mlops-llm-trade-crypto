# Makefile

.PHONY: run req help clean

req: ## Install requirements
	uv pip install -r pyproject.toml 
	uv lock

run: ## Run Trades Service App
	uv run python run.py

clean: ## Clean up generated files
	rm -rf __pycache__

help: ## Display this help message
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help