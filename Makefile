.PHONY: setup install test run run-dev ingest eval build-frontend docker-build docker-run

# Global Python alias
PYTHON := python

# Setup environment
setup:
	$(PYTHON) -m venv .venv
	@echo "Run 'source .venv/bin/activate' or '.venv\\Scripts\\activate' then 'make install'"

# Install dependencies
install:
	pip install -r requirements.txt
	cd frontend && npm install

# Build the React frontend
build-frontend:
	cd frontend && npm run build

# Run the backend API (serves built frontend)
run:
	$(PYTHON) api.py

# Run the backend API with hot-reloading (development)
run-dev:
	uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Full ingestion pipeline
ingest:
	$(PYTHON) ingest.py

# Run offline bundle checker
check-bundle:
	$(PYTHON) scripts/offline_bundle.py

# Run Python tests
test:
	$(PYTHON) -m pytest tests/ -v

# Run all evaluations
eval:
	$(PYTHON) -m eval.eval_retrieval
	$(PYTHON) -m eval.eval_grounding
	$(PYTHON) -m eval.eval_refusal
	$(PYTHON) -m eval.eval_latency

# Run ablation experiments
ablations:
	$(PYTHON) -m eval.run_ablations

# Docker commands
docker-build:
	docker build -t agribot:latest .

docker-run:
	docker-compose up -d
