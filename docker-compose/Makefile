# Makefile

.PHONY: start-redpanda stop-redpanda help


start-redpanda: ## Start single Redpanda broker and Redpanda Console
	docker compose -f redpanda.yml up -d

stop-redpanda: ## Stop single Redpanda broker and Redpanda Console
	docker compose -f redpanda.yml down


help: ## Display this help message
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
