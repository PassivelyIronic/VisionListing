"""
Ewaluacja modelu na golden dataset.

Uruchomienie:
    make test-evals

Wymaga:
    - uzupełnionego .env z kluczem API
    - zdjęć w backend/data/golden_dataset/
    - wypełnionego ground_truth.json

Każde zdjęcie jest wysyłane do API tylko raz — wyniki są cache'owane
w sesji pytest, żeby nie przekraczać rate limitu free tier.
"""

import json
import time
from pathlib import Path

import pytest

from app.llm.client import extract_listing
from app.models import ListingData

GOLDEN_DIR = Path(__file__).parent.parent.parent / "data" / "golden_dataset"
GROUND_TRUTH_FILE = GOLDEN_DIR / "ground_truth.json"
RATE_LIMIT_DELAY = 13  # sekundy między requestami (free tier: 5 req/min)

# Cache wyników w pamięci — klucz: image_path, wartość: ListingData | Exception
_results_cache: dict[Path, ListingData | Exception] = {}


def load_ground_truth() -> list[dict]:
    with open(GROUND_TRUTH_FILE) as f:
        return json.load(f)


def get_test_cases() -> list[tuple[Path, dict]]:
    cases = load_ground_truth()
    available = []
    for case in cases:
        image_path = GOLDEN_DIR / case["image_file"]
        if image_path.exists():
            available.append((image_path, case["expected"]))
    return available


def _media_type(path: Path) -> str:
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(path.suffix.lower(), "image/jpeg")


def get_result(image_path: Path) -> ListingData:
    """Pobiera wynik z cache lub wywołuje API (raz na zdjęcie)."""
    if image_path not in _results_cache:
        if _results_cache:
            time.sleep(RATE_LIMIT_DELAY)
        try:
            result = extract_listing(image_path.read_bytes(), _media_type(image_path))
            _results_cache[image_path] = result
        except Exception as e:
            _results_cache[image_path] = e

    cached = _results_cache[image_path]
    if isinstance(cached, Exception):
        pytest.skip(f"API error: {cached}")
    return cached


# --- Testy ewaluacyjne ---

@pytest.mark.parametrize("image_path,expected", get_test_cases())
def test_category_match(image_path: Path, expected: dict):
    """Kategoria musi być dokładnie zgodna z ground truth."""
    result = get_result(image_path)
    assert result.category == expected["category"], (
        f"[{image_path.name}] Oczekiwano: {expected['category']}, "
        f"Otrzymano: {result.category}"
    )


@pytest.mark.parametrize("image_path,expected", get_test_cases())
def test_price_variance(image_path: Path, expected: dict):
    """Cena musi mieścić się w 30% odchyleniu od ground truth."""
    result = get_result(image_path)
    expected_price = expected["estimated_price_pln"]
    tolerance = expected_price * 0.30
    diff = abs(result.estimated_price_pln - expected_price)
    assert diff <= tolerance, (
        f"[{image_path.name}] Cena poza tolerancją 30%: "
        f"oczekiwano {expected_price:.0f} PLN, "
        f"otrzymano {result.estimated_price_pln:.0f} PLN "
        f"(różnica: {diff:.0f} PLN)"
    )


@pytest.mark.parametrize("image_path,expected", get_test_cases())
def test_confidence_above_threshold(image_path: Path, expected: dict):
    """Model powinien być pewny swojej oceny (confidence > 0.5)."""
    result = get_result(image_path)
    assert result.confidence > 0.5, (
        f"[{image_path.name}] Zbyt niska pewność modelu: {result.confidence}"
    )


@pytest.mark.parametrize("image_path,expected", get_test_cases())
def test_title_not_empty(image_path: Path, expected: dict):
    """Tytuł nie może być pusty i musi mieć min. 10 znaków."""
    result = get_result(image_path)
    assert len(result.title) >= 10, (
        f"[{image_path.name}] Tytuł za krótki: '{result.title}'"
    )