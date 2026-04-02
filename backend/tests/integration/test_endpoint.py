import json
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models import Condition, ListingData

client = TestClient(app)

MOCK_LISTING = ListingData(
    title="iPhone 14 128GB Północ",
    description="Smartfon w bardzo dobrym stanie. Minimalne ślady użytkowania.",
    category="Electronics/Smartphones/Apple",
    estimated_price_pln=2200.0,
    condition=Condition.VERY_GOOD,
    confidence=0.91,
)

SAMPLE_IMAGE = b"\xff\xd8\xff\xe0" + b"\x00" * 100

SAMPLE_PAYLOAD = {
    "title": "iPhone 14 128GB Północ",
    "description": "Smartfon w bardzo dobrym stanie.",
    "category": "Electronics/Smartphones/Apple",
    "estimated_price_pln": 2200.0,
    "condition": "Bardzo dobry",
    "confidence": 0.91,
}


# --- /health ---

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "provider" in data


# --- /api/v1/extract-listing-info ---

@patch("app.router.extract_listing", return_value=MOCK_LISTING)
def test_extract_listing_success(mock_extract):
    response = client.post(
        "/api/v1/extract-listing-info",
        files={"image": ("phone.jpg", SAMPLE_IMAGE, "image/jpeg")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["title"] == "iPhone 14 128GB Północ"
    assert data["data"]["confidence"] == 0.91


@patch("app.router.extract_listing", return_value=MOCK_LISTING)
def test_extract_listing_returns_all_fields(mock_extract):
    response = client.post(
        "/api/v1/extract-listing-info",
        files={"image": ("phone.jpg", SAMPLE_IMAGE, "image/jpeg")},
    )
    data = response.json()["data"]
    for field in ["title", "description", "category", "estimated_price_pln", "condition", "confidence"]:
        assert field in data, f"Brak pola: {field}"


def test_extract_listing_unsupported_format():
    response = client.post(
        "/api/v1/extract-listing-info",
        files={"image": ("doc.pdf", b"%PDF", "application/pdf")},
    )
    assert response.status_code == 415


def test_extract_listing_empty_file():
    response = client.post(
        "/api/v1/extract-listing-info",
        files={"image": ("empty.jpg", b"", "image/jpeg")},
    )
    assert response.status_code == 400


@patch("app.router.extract_listing", side_effect=json.JSONDecodeError("err", "", 0))
def test_extract_listing_llm_bad_json(mock_extract):
    response = client.post(
        "/api/v1/extract-listing-info",
        files={"image": ("phone.jpg", SAMPLE_IMAGE, "image/jpeg")},
    )
    assert response.status_code == 502


# --- /api/v1/listings ---

def test_publish_listing_success():
    response = client.post("/api/v1/listings", json=SAMPLE_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "id" in data


def test_get_listings_returns_list():
    client.post("/api/v1/listings", json=SAMPLE_PAYLOAD)
    response = client.get("/api/v1/listings")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 1


def test_published_listing_has_required_fields():
    client.post("/api/v1/listings", json=SAMPLE_PAYLOAD)
    response = client.get("/api/v1/listings")
    item = response.json()["data"][0]
    for field in ["id", "title", "category", "price_pln", "condition", "created_at"]:
        assert field in item, f"Brak pola: {field}"