# Makefile

.PHONY: req run-dev build run clean ruff help

req: ## Install requirements
	uv pip install -r pyproject.toml --all-extras
	uv lock

run-dev: ## Run Trades Service App
	uv run python run.py

# This image is optimized for production use
build: ## Build the Docker image (optimized)
	docker build -f Dockerfile -t candles .

run: build ## Run (optimized) the Docker container using the internal port (see redpanda.yml, advertise-kafka-addr)
	docker run -it \
		--network redpanda_network \
		-e KAFKA_BROKER_ADDRESS=redpanda:9092 \
		candles

ruff: ## Run Ruff linter
	ruff check . --fix --exit-non-zero-on-fix --show-fixes

clean: ## Clean up generated files
	rm -rf __pycache__
	rm -rf .ruff_cache

help: ## Display this help message
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
