# quick-sell ⚡

Marketplace ogłoszeń dla **używanej elektroniki** z AI Pre-filling.

Wgrywasz zdjęcie urządzenia → AI automatycznie uzupełnia tytuł, opis, kategorię, cenę i stan.

![Demo](docs/demo.gif)
<!-- TODO: nagrać demo i wrzucić tutaj -->

---

## Co robi ten projekt

| Funkcja | Opis |
|---|---|
| 📸 Vision LLM | Analizuje zdjęcie i ekstrahuje dane o przedmiocie |
| 🏷️ Structured Output | Zwraca JSON z walidacją schematu (Pydantic) |
| ⚙️ Multi-provider | Obsługa Anthropic i OpenAI — konfigurowalne przez `.env` |
| 🧪 Testy | Unit, integracyjne i LLM-as-judge evaluation |
| 🚀 CI/CD | GitHub Actions z lintem i testami |

---

## Szybki start

```bash
# 1. Sklonuj repo
git clone https://github.com/TWOJ_NICK/quick-sell.git
cd quick-sell

# 2. Utwórz środowisko conda
conda env create -f environment.yml
conda activate quick-sell

# 3. Skonfiguruj klucze API
cp .env.example .env
# Edytuj .env i wpisz swój klucz API

# 4. Uruchom backend
make run-backend

# 5. W nowym terminalu uruchom frontend
make run-frontend
```

Backend dostępny na: http://localhost:8000  
Frontend dostępny na: http://localhost:8501  
Swagger UI: http://localhost:8000/docs

---

## Endpoint API

```
POST /api/v1/extract-listing-info
Content-Type: multipart/form-data

Parametry: image (plik)
```

Przykładowa odpowiedź:
```json
{
  "status": "success",
  "data": {
    "title": "MacBook Air M1 8GB/256GB Space Gray",
    "description": "Laptop w bardzo dobrym stanie. Minimalne ślady użytkowania na obudowie...",
    "category": "Electronics/Laptops/Apple",
    "estimated_price_pln": 3200.00,
    "condition": "Bardzo dobry",
    "confidence": 0.91
  }
}
```

---

## Testy i ewaluacja

```bash
make test-unit      # testy logiki backendu (bez API)
make test-int       # testy endpointu z prawdziwym API
make test-evals     # LLM-as-judge na golden dataset
```

---

## Konfiguracja modelu

Zmień providera i model bez zmiany kodu:

```env
# .env
MODEL_PROVIDER=anthropic          # lub: openai
ANTHROPIC_MODEL=claude-3-5-haiku-20241022   # tańszy
# ANTHROPIC_MODEL=claude-3-5-sonnet-20241022 # dokładniejszy
```

---

## Struktura projektu

```
quick-sell/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── config.py        # ustawienia z .env
│   │   ├── models.py        # Pydantic schemas
│   │   ├── router.py        # endpoint /extract-listing-info
│   │   └── llm/
│   │       ├── client.py    # abstrakcja nad providerami
│   │       └── prompts.py   # system prompt
│   ├── tests/
│   │   ├── unit/            # testy bez API
│   │   ├── integration/     # testy endpointu
│   │   └── evals/           # LLM evaluation
│   └── data/
│       └── golden_dataset/  # ground truth JSON + zdjęcia
├── frontend/
│   └── app.py               # Streamlit UI
├── .github/workflows/
│   └── ci.yml               # GitHub Actions
├── environment.yml           # conda dependencies
├── Makefile
└── .env.example
```
