# Makefile

.PHONY: req run-dev build run clean_cache ruff help

req: ## Install requirements
	uv pip install -r pyproject.toml --all-extras
	uv lock


# ===== DEVELOPMENT =====
run-dev-live: ## Run Live News Signal Service App
	cp live.settings.env settings.env
	uv run python run.py

run-dev-historical: ## Run Historical News Signal Service Ap
	cp historical.settings.env settings.env
	uv run python run.py


run-claude: ## Run Claude
	uv run python llms/claude.py

run-ollama: ## Run Ollama
	uv run python llms/ollama_model.py


# ===== DATASET GENERATION =====
# Generation of an instruction dataset with tuples (instruction, input, output)
# to do Supervised Fine Tuning
instruction-dataset-with-claude: ## Generate instruction dataset with Claude
	uv run python golden_dataset.py \
		--llm_name anthropic \
		--n 10 \
		--input_file ./data/cryptopanic_news.csv \
		--output_file ./data/instruction_dataset_claude_10k.jsonl

instruction-dataset-with-ollama: ## Generate instruction dataset with Ollama
	uv run python golden_dataset.py \
		--llm_name ollama \
		--n 100 \
		--input_file ./data/cryptopanic_news.csv \
		--output_file ./data/instruction_dataset_ollama_10k.jsonl


# ===== DOCKER =====
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

# ===== FINE TUNING =====
# To install the dependencies for the GPU instance
venv-gpu-instance:
	curl -LsSf https://astral.sh/uv/install.sh | sh && \
	source $HOME/.local/bin/env && \
	uv sync --group gpu-instance

# To login to Comet ML during fine-tuning
login-comet:
	uv run comet login

# To fine-tune the model unsloth/Llama-3.2-1B-bnb-4bit, unsloth/Qwen2.5-0.5B-bnb-4bit, unsloth/gemma-2-2b-bnb-4bit
fine-tune: ## Fine-tune the model
	uv run python fine_tuning.py \
		--base_llm_name unsloth/Qwen2.5-0.5B-bnb-4bit \
		--dataset_path ./data/instruction_dataset_ollama_10k.jsonl \
		--comet_ml_project_name news-signal-extractor \
		--max_steps 100 --debug


# ===== HELPERS =====
ruff: ## Run Ruff linter
	ruff check . --fix --exit-non-zero-on-fix --show-fixes --exclude llama.cpp

clean_cache: ## Clean up generated files
	rm -rf __pycache__
	rm -rf .ruff_cache

help: ## Display this help message
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
