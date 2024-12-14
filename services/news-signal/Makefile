# Makefile

.PHONY: req run-dev build run clean ruff help

req: ## Install requirements
	uv pip install -r pyproject.toml --all-extras
	uv lock

run-dev: ## Run News Signal Service App
	uv run python run.py

run-claude: ## Run Claude
	uv run python llms/claude.py

run-ollama: ## Run Ollama
	uv run python llms/ollama_model.py

# This image is optimized for production use
build: ## Build the Docker image (optimized)
	docker build -f Dockerfile -t news-signal .

run-with-anthropic: build ## Run with Claude
	docker run -it \
			--network redpanda_network \
    		-e KAFKA_BROKER_ADDRESS=redpanda:9092 \
			-e MODEL=anthropic \
			--env-file anthropic_credentials.env \
    		-v news_signal_named_volume:/app/state \
			news-signal:latest

run-with-ollama: build ## Run with Ollama
	docker run -it \
			--network redpanda_network \
    		-e KAFKA_BROKER_ADDRESS=redpanda:9092 \
			--env-file ollama.env \
			-e MODEL=ollama \
			-v news_signal_named_volume:/app/state \
			news-signal:latest

ruff: ## Run Ruff linter
	ruff check . --fix --exit-non-zero-on-fix --show-fixes

clean: ## Clean up generated files
	rm -rf __pycache__
	rm -rf .ruff_cache

help: ## Display this help message
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
