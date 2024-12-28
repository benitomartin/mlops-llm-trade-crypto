# Makefile

.PHONY: req training clean ruff help

reset-venv: ## Reset virtual environment
	uv clean
	rm -rf .venv
	rm uv.lock
	uv sync

req: ## Install requirements
	uv pip install -r pyproject.toml --all-extras
	uv lock

training: ## Run training
	uv run python training.py

inference: ## Run inference 
	uv run python inference.py

build: ## Build the price predictor docker image
	docker build -f Dockerfile -t price-predictor .

run-training: build ## Run the dockerized trainining job
	-docker rm -f price-predictor-training || true
	docker run -it \
		--name price-predictor-training \
		-e TRAINING_OR_INFERENCE=training \
		-v price_predictor_named_volume:/app/state \
		price-predictor:latest

# Must be run with the redpanda network, the elastic search and tht technical indicators live service
run-inference: build ## Run the dockerized inference job
	-docker rm -f price-predictor-inference || true
	docker run -it \
		--name price-predictor-inference \
		-e TRAINING_OR_INFERENCE=inference \
		--network redpanda_network \
		-e KAFKA_BROKER_ADDRESS=redpanda:9092 \
		-e ELASTICSEARCH_URL=http://elasticsearch:9200 \
		-v price_predictor_named_volume:/app/state \
		price-predictor:latest

ruff: ## Run Ruff linter
	ruff check . --fix --exit-non-zero-on-fix --show-fixes

clean: ## Clean up generated files
	rm -rf __pycache__
	rm -rf .ruff_cache

help: ## Display this help message
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
