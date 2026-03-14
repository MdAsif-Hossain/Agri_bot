.PHONY: setup install test run run-dev ingest build-frontend

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

# Run Python tests
test:
	$(PYTHON) -m pytest tests/ -v
