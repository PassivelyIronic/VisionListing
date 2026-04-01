"""
Ewaluacja modelu na golden dataset.

Uruchomienie:
    make test-evals

Wymaga:
    - uzupełnionego .env z kluczem API
    - zdjęć w backend/data/golden_dataset/
    - wypełnionego ground_truth.json
"""

import json
from pathlib import Path

import pytest

from app.llm.client import extract_listing
from app.models import ListingData

GOLDEN_DIR = Path(__file__).parent.parent.parent / "data" / "golden_dataset"
GROUND_TRUTH_FILE = GOLDEN_DIR / "ground_truth.json"


def load_ground_truth() -> list[dict]:
    with open(GROUND_TRUTH_FILE) as f:
        return json.load(f)


def get_test_cases():
    cases = load_ground_truth()
    available = []
    for case in cases:
        image_path = GOLDEN_DIR / case["image_file"]
        if image_path.exists():
            available.append((image_path, case["expected"]))
    return available


# --- Testy ewaluacyjne ---

@pytest.mark.parametrize("image_path,expected", get_test_cases())
def test_category_match(image_path: Path, expected: dict):
    """Kategoria musi być dokładnie zgodna z ground truth."""
    image_bytes = image_path.read_bytes()
    media_type = _media_type(image_path)

    result: ListingData = extract_listing(image_bytes, media_type)

    assert result.category == expected["category"], (
        f"[{image_path.name}] Oczekiwano: {expected['category']}, "
        f"Otrzymano: {result.category}"
    )


@pytest.mark.parametrize("image_path,expected", get_test_cases())
def test_price_variance(image_path: Path, expected: dict):
    """Cena musi mieścić się w 30% odchyleniu od ground truth."""
    image_bytes = image_path.read_bytes()
    media_type = _media_type(image_path)

    result: ListingData = extract_listing(image_bytes, media_type)

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
    image_bytes = image_path.read_bytes()
    media_type = _media_type(image_path)

    result: ListingData = extract_listing(image_bytes, media_type)

    assert result.confidence > 0.5, (
        f"[{image_path.name}] Zbyt niska pewność modelu: {result.confidence}"
    )


@pytest.mark.parametrize("image_path,expected", get_test_cases())
def test_title_not_empty(image_path: Path, expected: dict):
    """Tytuł nie może być pusty i musi mieć min. 10 znaków."""
    image_bytes = image_path.read_bytes()
    media_type = _media_type(image_path)

    result: ListingData = extract_listing(image_bytes, media_type)

    assert len(result.title) >= 10, (
        f"[{image_path.name}] Tytuł za krótki: '{result.title}'"
    )


# --- Helper ---

def _media_type(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(suffix, "image/jpeg")