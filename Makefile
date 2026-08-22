.PHONY: help install install-dev test test-cov lint format run-frontend run-backend docker-build docker-up clean

help:
	@echo "UnderwriteAI Enterprise Intelligence Platform"
	@echo "Available commands:"
	@echo "  make install        - Install Python and Node dependencies"
	@echo "  make install-dev    - Install development dependencies"
	@echo "  make test           - Run full test suite with pytest"
	@echo "  make test-cov       - Run pytest with coverage report"
	@echo "  make lint           - Check code formatting and linting with Ruff"
	@echo "  make format         - Auto-format code with Black and Ruff"
	@echo "  make run-frontend   - Launch React Enterprise single-page UI (port 5173)"
	@echo "  make run-backend    - Launch FastAPI REST API server (port 8000)"
	@echo "  make docker-build   - Build Docker container image"
	@echo "  make docker-up      - Start containers via docker-compose"
	@echo "  make clean          - Remove temporary caches and build artifacts"

install:
	pip install -r requirements.txt
	cd frontend-react && npm install

install-dev:
	pip install -r requirements-dev.txt
	cd frontend-react && npm install

test:
	pytest -v

test-cov:
	pytest -v --cov=backend --cov-report=term-missing

lint:
	ruff check .

format:
	black backend tests
	ruff check --fix .

run-frontend:
	cd frontend-react && npm run dev

run-backend:
	python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

docker-build:
	docker build -t underwrite-ai:latest .

docker-up:
	docker-compose up -d

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov
