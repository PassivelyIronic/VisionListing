import json

import pytest
from pydantic import ValidationError

from app.models import Condition, ListingData, ListingResponse


# --- ListingData ---

def test_listing_data_valid():
    data = ListingData(
        title="iPhone 13 128GB Czarny",
        description="Stan bardzo dobry, brak rys.",
        category="Electronics/Smartphones/Apple",
        estimated_price_pln=1800.0,
        condition=Condition.VERY_GOOD,
        confidence=0.92,
    )
    assert data.title == "iPhone 13 128GB Czarny"
    assert data.condition == Condition.VERY_GOOD


def test_listing_data_confidence_bounds():
    with pytest.raises(ValidationError):
        ListingData(
            title="Test",
            description="Test",
            category="Electronics/Other",
            estimated_price_pln=100.0,
            condition=Condition.GOOD,
            confidence=1.5,  # powyżej 1.0 — powinno rzucić błąd
        )


def test_listing_data_invalid_condition():
    with pytest.raises(ValidationError):
        ListingData(
            title="Test",
            description="Test",
            category="Electronics/Other",
            estimated_price_pln=100.0,
            condition="Zniszczony",  # nie ma w Enum
            confidence=0.5,
        )


# --- ListingResponse ---

def test_listing_response_structure():
    response = ListingResponse(
        status="success",
        data=ListingData(
            title="Samsung Galaxy S22",
            description="Dobry stan, lekkie rysy.",
            category="Electronics/Smartphones/Android",
            estimated_price_pln=950.0,
            condition=Condition.GOOD,
            confidence=0.85,
        ),
    )
    assert response.status == "success"
    assert response.data.estimated_price_pln == 950.0


# --- _parse_response (logika parsowania JSON z LLM) ---

from app.llm.client import _parse_response


def test_parse_response_clean_json():
    raw = json.dumps({
        "title": "MacBook Air M2",
        "description": "Bardzo dobry stan.",
        "category": "Electronics/Laptops/Apple",
        "estimated_price_pln": 4500.0,
        "condition": "Bardzo dobry",
        "confidence": 0.95,
    })
    result = _parse_response(raw)
    assert result.title == "MacBook Air M2"
    assert result.confidence == 0.95


def test_parse_response_strips_markdown_fences():
    raw = """```json
{
  "title": "Sony WH-1000XM5",
  "description": "Słuchawki w nowym stanie.",
  "category": "Electronics/Headphones",
  "estimated_price_pln": 950.0,
  "condition": "Nowy",
  "confidence": 0.88
}
```"""
    result = _parse_response(raw)
    assert result.title == "Sony WH-1000XM5"


def test_parse_response_invalid_json_raises():
    with pytest.raises(json.JSONDecodeError):
        _parse_response("to nie jest json")