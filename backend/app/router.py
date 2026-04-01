import json

from fastapi import APIRouter, HTTPException, UploadFile

from app.llm.client import extract_listing
from app.models import ListingResponse

router = APIRouter(prefix="/api/v1")

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}


@router.post("/extract-listing-info", response_model=ListingResponse)
async def extract_listing_info(image: UploadFile) -> ListingResponse:
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Nieobsługiwany format pliku: {image.content_type}. Dozwolone: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )

    image_bytes = await image.read()

    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Plik jest pusty.")

    try:
        listing_data = extract_listing(image_bytes, image.content_type)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Model zwrócił nieprawidłowy JSON: {e}",
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ListingResponse(status="success", data=listing_data)