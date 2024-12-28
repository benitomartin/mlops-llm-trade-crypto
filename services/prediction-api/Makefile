# Makefile

.PHONY: help clean clean-state ruff hooks


run: ## Cargo run
	cargo run

check-health: ## Check health endpoint
	curl http://127.0.0.1:8080/health

eth-prediction: ## Get ETH prediction
	curl "http://127.0.0.1:8080/predict?pair=ETH%2FUSD"

btc-prediction:	## Get BTC prediction
	curl "http://127.0.0.1:8080/predict?pair=BTC%2FUSD"

help: ## Display this help message
	@echo "Default target: $(.DEFAULT_GOAL)"
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help