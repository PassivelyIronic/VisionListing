.PHONY: help env setup lint test test-unit test-integration test-evals run-backend run-frontend

help:
	@echo "Dostępne komendy:"
	@echo "  make env           - utwórz środowisko conda"
	@echo "  make setup         - aktywuj env i zainstaluj zależności"
	@echo "  make lint          - sprawdź jakość kodu (ruff)"
	@echo "  make test          - uruchom wszystkie testy"
	@echo "  make test-unit     - tylko unit testy"
	@echo "  make test-int      - tylko testy integracyjne"
	@echo "  make test-evals    - ewaluacja LLM (wymaga klucza API)"
	@echo "  make run-backend   - uruchom serwer FastAPI"
	@echo "  make run-frontend  - uruchom Streamlit"

env:
	conda env create -f environment.yml

setup:
	conda env update -f environment.yml --prune

lint:
	cd backend && ruff check app/ tests/

test:
	cd backend && pytest tests/ -v --cov=app --cov-report=term-missing

test-unit:
	cd backend && pytest tests/unit/ -v

test-int:
	cd backend && pytest tests/integration/ -v

test-evals:
	cd backend && pytest tests/evals/ -v -s

run-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

run-frontend:
	cd frontend && streamlit run app.py
