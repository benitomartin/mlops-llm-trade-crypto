# Makefile

.PHONY: req run-dev build run clean ruff help build-multi run-multi build-naive run-naive

req: ## Install requirements
	uv pip install -r pyproject.toml --all-extras
	uv lock

run-dev-live: ## Run Trades Service App (Live)
	cp live.settings.env settings.env
	uv run python run.py

run-dev-historical: ## Run Trades Service App (Historical)
	cp historical.settings.env settings.env
	uv run python run.py


# This image is more optimized for production use, as it is a multi-stage build and
# reduces the size of the final image
build: ## Build the Docker image (Multistage)
	docker build -f multistage.Dockerfile -t trades .

run: build ## Run (Multistage) the Docker container using the internal port (see redpanda.yml, advertise-kafka-addr)
	 docker run -it \
		--network redpanda_network \
		-e KAFKA_BROKER_ADDRESS=redpanda:9092 \
		trades

ruff: ## Run Ruff linter
	ruff check . --fix --exit-non-zero-on-fix --show-fixes

clean: ## Clean up generated files
	rm -rf __pycache__
	rm -rf .ruff_cache

help: ## Display this help message
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help


# #-------#
# # This image is optimized for production use
# build-standard: ## Build the Docker image (optimized)
# 	docker build -f Dockerfile -t trades_standard .

# run-standard: build-standard ## Run (optimized) the Docker container using the internal port (see redpanda.yml, advertise-kafka-addr)
# 			  docker run -it \
# 				--network redpanda_network \
# 				-e KAFKA_BROKER_ADDRESS=redpanda:9092 \
# 				trades_standard
# #-------#

# #-------#
# # This image is not optimized for production use, it is just for testing purposes
# build-naive: ## Build the Docker image (naive)
# 	docker build -f naive.Dockerfile -t trades_naive .

# run-naive: build-naive ## Run (naive) the Docker container using the internal port (see redpanda.yml, advertise-kafka-addr)
# 		   docker run -it \
# 				--network redpanda_network \
# 				-e KAFKA_BROKER_ADDRESS=redpanda:9092 \
# 				trades_naive
# #-------#