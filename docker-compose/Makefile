# Makefile

.PHONY: start-redpanda stop-redpanda help


# ===== REDPANDA =====
start-redpanda: ## Start single Redpanda broker and Redpanda Console
	docker compose -f redpanda.yml up -d

stop-redpanda: ## Stop single Redpanda broker and Redpanda Console
	docker compose -f redpanda.yml down

add-one-partition-to-trades-topic: ## Add one partition to the trades topic
	docker compose -f redpanda.yml exec redpanda rpk topic add-partitions trades --num 1


# ===== LIVE PIPELINE =====
build-technical-indicators-live: ## Build the live technical indicators pipeline
	docker compose -f technical-indicators-live.yml build

start-technical-indicators-live: build-technical-indicators-live ## Start the live technical indicators pipeline
	docker compose -f technical-indicators-live.yml up -d

stop-technical-indicators-live: ## Stop the live technical indicators pipeline
	docker compose -f technical-indicators-live.yml down


# ===== HISTORICAL PIPELINE =====
build-technical-indicators-historical: ## Build the historical technical indicators pipeline
	docker compose -f technical-indicators-historical.yml build

start-technical-indicators-historical: build-technical-indicators-historical ## Start the historical technical indicators pipeline
	docker compose -f technical-indicators-historical.yml up -d

stop-technical-indicators-historical: ## Stop the historical technical indicators pipeline
	docker compose -f technical-indicators-historical.yml down


# ===== BACKFILL TECHNICAL INDICATORS =====
# Generates a unique RUN_ID for each backfill using the uuidgen command

backfill-technical-indicators: build-technical-indicators-historical ## Start the backfill historical technical indicators pipeline
	$(eval RUN_ID := $(shell uuidgen))
	@echo "Starting backfill with RUN_ID: $(RUN_ID)"
	RUN_ID=$(RUN_ID) docker compose -f technical-indicators-historical.yml up -d


# ===== NEWS SIGNAL LIVE =====
# LIVE News signal pipeline management
build-news-signal-live: ## Build the live news signal pipeline
	docker compose -f news-signal-live.yml build

start-news-signal-live: build-news-signal-live ## Start the live news signal pipeline
	docker compose -f news-signal-live.yml up -d

stop-news-signal-live: ## Stop the live news signal pipeline
	docker compose -f news-signal-live.yml down


# ===== NEWS SIGNAL HISTORICAL =====
# HISTORICAL News signal pipeline management
build-news-signal-historical: ## Build the historical news signal pipeline
	docker compose -f news-signal-historical.yml build

backfill-news-signals: build-news-signal-historical ## Start the backfill news signal pipeline
	$(eval RUN_ID := $(shell uuidgen))
	@echo "Starting backfill of news signals with RUN_ID: $(RUN_ID)"
	RUN_ID=$(RUN_ID) docker compose -f news-signal-historical.yml up -d

stop-news-signal-historical: ## Stop the historical news signal pipeline
	docker compose -f news-signal-historical.yml down

# ===== CLEANING BACKFILL =====
# Remove unused Kafka topic after backfill operations
clean-backfill-kakfa-topics: ## Remove unused Kafka topic after backfill operations
	@echo "Removing all Kafka topics that contain the word historical"
	docker compose -f redpanda.yml exec redpanda rpk topic delete -r ".*historical.*"

# ===== HELP =====
help: ## Display this help message
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
