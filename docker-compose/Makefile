# Makefile

.PHONY: start-redpanda stop-redpanda help

start-redpanda: ## Start single Redpanda broker and Redpanda Console
	docker compose -f redpanda.yml up -d

stop-redpanda: ## Stop single Redpanda broker and Redpanda Console
	docker compose -f redpanda.yml down

add-one-partition-to-trades-topic: ## Add one partition to the trades topic
	docker compose -f redpanda.yml exec redpanda rpk topic add-partitions trades --num 1

help: ## Display this help message
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
