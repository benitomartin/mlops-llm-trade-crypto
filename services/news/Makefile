# Makefile

.PHONY: req run-dev build run clean ruff help

req: ## Install requirements
	uv pip install -r pyproject.toml --all-extras
	uv lock


run-dev-live: ## Run Live News Service App
	cp live.settings.env settings.env
	uv run python run.py

run-dev-historical: ## Run Historical News Service App
	cp historical.settings.env settings.env
	uv run python run.py


# This image is optimized for production use
build: ## Build the Docker image (optimized)
	docker build -f Dockerfile -t news .

run: build ## Run (optimized) the Docker container using the internal port (see redpanda.yml, advertise-kafka-addr)
	docker run -it \
			--network redpanda_network \
    		-e KAFKA_BROKER_ADDRESS=redpanda:9092 \
			--env-file cryptopanic_credentials.env \
    		-v news_named_volume:/app/state \
			news:latest

ruff: ## Run Ruff linter
	ruff check . --fix --exit-non-zero-on-fix --show-fixes

clean: ## Clean up generated files
	rm -rf __pycache__
	rm -rf .ruff_cache
	rm -rf .mypy_cache

help: ## Display this help message
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
