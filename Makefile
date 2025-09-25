# Pipecat Agent Builder Makefile

.PHONY: help install setup clean test run vectorize deploy

help:
	@echo "Pipecat Agent Builder - Available commands:"
	@echo ""
	@echo "  install     - Install dependencies"
	@echo "  setup       - Run complete setup process"
	@echo "  clean       - Clean generated files and caches"
	@echo "  test        - Run tests"
	@echo "  run         - Start the agent builder"
	@echo "  vectorize   - Vectorize documentation"
	@echo "  deploy      - Deploy example agent"
	@echo "  dev         - Start in development mode"
	@echo ""

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

setup:
	@echo "Running setup..."
	python setup.py

clean:
	@echo "Cleaning up..."
	rm -rf data/chroma_db/*
	rm -rf generated_agents/*
	rm -rf logs/*
	rm -rf __pycache__
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

test:
	@echo "Running tests..."
	pytest tests/ -v

run:
	@echo "Starting Pipecat Agent Builder..."
	python main.py

vectorize:
	@echo "Vectorizing documentation..."
	python scripts/vectorize_docs.py

dev:
	@echo "Starting in development mode..."
	DEBUG=true python main.py

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker build -t pipecat-agent-builder .

docker-run:
	@echo "Running in Docker..."
	docker run -it --rm -p 8000:8000 -v $(PWD)/.env:/app/.env pipecat-agent-builder

# Deployment helpers
check-env:
	@echo "Checking environment variables..."
	@python -c "from core.config import settings; print('✅ Configuration loaded successfully')"

check-docker:
	@echo "Checking Docker..."
	@docker --version || echo "❌ Docker not found"

check-apis:
	@echo "Checking API connectivity..."
	@python -c "import asyncio; from core.config import settings; print('API keys configured:', bool(settings.openai_api_key and settings.deepgram_api_key and settings.cartesia_api_key))"
