# quick-sell

Marketplace ogłoszeń dla używanej elektroniki z AI pre-filling.

Wgrywasz zdjęcie urządzenia — model vision automatycznie uzupełnia tytuł, opis, kategorię, cenę i stan. Użytkownik weryfikuje i publikuje ogłoszenie.

![Demo](docs/demo.gif)

---

## Stack

- **Backend:** FastAPI + Pydantic
- **AI:** Google Gemini 2.5 Flash (vision + structured output) — obsługa Anthropic i OpenAI przez zmianę zmiennej w `.env`
- **Frontend:** Streamlit
- **Testy:** pytest — unit, integracyjne, ewaluacja na golden dataset (21 pozycji)
- **CI/CD:** GitHub Actions

---

## Szybki start

```bash
git clone https://github.com/TWOJ_NICK/quick-sell.git
cd quick-sell

conda env create -f environment.yml
conda activate quick-sell

cp .env.example .env
# uzupełnij klucz API w .env

make run-backend    # http://localhost:8000
make run-frontend   # http://localhost:8501
```

Swagger UI: http://localhost:8000/docs

---

## API

```
POST /api/v1/extract-listing-info
Content-Type: multipart/form-data
```

```json
{
  "status": "success",
  "data": {
    "title": "Dell XPS 13 Ultrabook Premium",
    "description": "Laptop w dobrym stanie. Smukła konstrukcja z ekranem InfinityEdge...",
    "category": "Electronics/Laptops/Windows",
    "estimated_price_pln": 1300.00,
    "condition": "Dobry",
    "confidence": 0.88
  }
}
```

---

## Testy

```bash
make test-unit      # testy logiki backendu bez API
make test-int       # testy endpointu z mock LLM
make test-evals     # ewaluacja modelu na golden dataset (wymaga zdjęć lokalnie)
```

Ewaluacja sprawdza: dokładność kategorii, odchylenie ceny (tolerancja ±30%), pewność modelu i poprawność tytułu.

---

## Zmiana providera

```env
# .env
MODEL_PROVIDER=google
GOOGLE_MODEL=gemini-2.5-flash

# MODEL_PROVIDER=anthropic
# ANTHROPIC_MODEL=claude-3-5-haiku-20241022

# MODEL_PROVIDER=openai
# OPENAI_MODEL=gpt-4o-mini
```

---

## Struktura

```
quick-sell/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── router.py
│   │   └── llm/
│   │       ├── client.py       # abstrakcja nad providerami
│   │       └── prompts.py      # system prompt
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── evals/
│   └── data/
│       └── golden_dataset/     # 21 ręcznie zweryfikowanych pozycji
├── frontend/
│   └── app.py
├── scripts/
│   └── build_golden_dataset.py
├── .github/workflows/ci.yml
├── environment.yml
├── Makefile
└── .env.example
```