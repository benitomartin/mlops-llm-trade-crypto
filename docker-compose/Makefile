# Makefile

.PHONY: start-redpanda stop-redpanda help

start-redpanda: ## Start single Redpanda broker and Redpanda Console
	docker compose -f redpanda.yml up -d

stop-redpanda: ## Stop single Redpanda broker and Redpanda Console
	docker compose -f redpanda.yml down

add-one-partition-to-trades-topic: ## Add one partition to the trades topic
	docker compose -f redpanda.yml exec redpanda rpk topic add-partitions trades --num 1

build-technical-indicators-pipeline: ## Build the technical indicators pipeline
	docker compose -f technical-indicators-pipeline.yml build

start-technical-indicators-pipeline: ## Start the technical indicators pipeline
	$(MAKE) build-technical-indicators-pipeline
	docker compose -f technical-indicators-pipeline.yml up -d

stop-technical-indicators-pipeline: ## Stop the technical indicators pipeline
	docker compose -f technical-indicators-pipeline.yml down

help: ## Display this help message
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
