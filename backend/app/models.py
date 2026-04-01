from enum import Enum

from pydantic import BaseModel, Field


class Condition(str, Enum):
    NEW = "Nowy"
    VERY_GOOD = "Bardzo dobry"
    GOOD = "Dobry"
    ACCEPTABLE = "Akceptowalny"
    FOR_REPAIR = "Do naprawy"


class ListingData(BaseModel):
    title: str = Field(description="Tytuł ogłoszenia, maks. 60 znaków")
    description: str = Field(description="Opis przedmiotu, 2-4 zdania")
    category: str = Field(description="Kategoria w formacie: Electronics/Laptops/Apple")
    estimated_price_pln: float = Field(description="Szacowana cena w PLN na rynku wtórnym")
    condition: Condition = Field(description="Stan przedmiotu")
    confidence: float = Field(ge=0.0, le=1.0, description="Pewność oceny modelu (0.0 - 1.0)")


class ListingResponse(BaseModel):
    status: str
    data: ListingData