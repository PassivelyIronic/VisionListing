import base64
import json

import anthropic
import openai
from google import genai
from google.genai import types

from app.config import settings
from app.llm.prompts import SYSTEM_PROMPT
from app.models import ListingData


def _image_to_base64(image_bytes: bytes) -> str:
    return base64.standard_b64encode(image_bytes).decode("utf-8")


def _parse_response(raw_text: str) -> ListingData:
    cleaned = raw_text.strip().removeprefix("```json").removesuffix("```").strip()
    data = json.loads(cleaned)
    return ListingData(**data)


def extract_listing_anthropic(image_bytes: bytes, media_type: str) -> ListingData:
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    message = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": _image_to_base64(image_bytes),
                        },
                    },
                    {
                        "type": "text",
                        "text": "Przeanalizuj to zdjęcie i zwróć dane ogłoszenia jako JSON.",
                    },
                ],
            }
        ],
    )

    return _parse_response(message.content[0].text)


def extract_listing_openai(image_bytes: bytes, media_type: str) -> ListingData:
    client = openai.OpenAI(api_key=settings.openai_api_key)

    b64 = _image_to_base64(image_bytes)
    data_url = f"data:{media_type};base64,{b64}"

    response = client.chat.completions.create(
        model=settings.openai_model,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_url}},
                    {
                        "type": "text",
                        "text": "Przeanalizuj to zdjęcie i zwróć dane ogłoszenia jako JSON.",
                    },
                ],
            },
        ],
    )

    return _parse_response(response.choices[0].message.content)


def extract_listing_google(image_bytes: bytes, media_type: str) -> ListingData:
    client = genai.Client(api_key=settings.google_api_key)

    response = client.models.generate_content(
        model=settings.google_model,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=media_type),
            "Przeanalizuj to zdjęcie i zwróć dane ogłoszenia jako JSON.",
        ],
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
    )

    return _parse_response(response.text)


def extract_listing(image_bytes: bytes, media_type: str) -> ListingData:
    """Główna funkcja — wybiera provider na podstawie settings.model_provider."""
    if settings.model_provider == "anthropic":
        return extract_listing_anthropic(image_bytes, media_type)
    elif settings.model_provider == "openai":
        return extract_listing_openai(image_bytes, media_type)
    elif settings.model_provider == "google":
        return extract_listing_google(image_bytes, media_type)
    else:
        raise ValueError(f"Nieznany provider: {settings.model_provider}")