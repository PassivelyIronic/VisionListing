import json

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import ValidationError

from app.database import get_listings, save_listing
from app.llm.client import extract_listing
from app.models import (
    ListingResponse,
    ListingSaveRequest,
    ListingSaveResponse,
    ListingsResponse,
    PublishedListing,
)

router = APIRouter(prefix="/api/v1")

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


@router.post("/extract-listing-info", response_model=ListingResponse)
async def extract_listing_info(image: UploadFile) -> ListingResponse:
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Nieobsługiwany format: {image.content_type}. Dozwolone: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )

    image_bytes = await image.read()

    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Plik jest pusty.")

    try:
        listing_data = extract_listing(image_bytes, image.content_type)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=502, detail=f"Model zwrócił nieprawidłowy JSON: {e}")
    except ValidationError as e:
        raise HTTPException(status_code=502, detail=f"Model zwrócił nieprawidłowe dane: {e}")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ListingResponse(status="success", data=listing_data)


@router.post("/listings", response_model=ListingSaveResponse)
def publish_listing(payload: ListingSaveRequest) -> ListingSaveResponse:
    listing_id = save_listing(
        title=payload.title,
        description=payload.description,
        category=payload.category,
        price_pln=payload.estimated_price_pln,
        condition=payload.condition,
        confidence=payload.confidence,
    )
    return ListingSaveResponse(status="success", id=listing_id)


@router.get("/listings", response_model=ListingsResponse)
def list_listings() -> ListingsResponse:
    rows = get_listings()
    listings = [PublishedListing(**row) for row in rows]
    return ListingsResponse(status="success", data=listings)