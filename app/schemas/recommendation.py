from pydantic import BaseModel, Field
from typing import Optional


class RecommendationRequest(BaseModel):

    preferensi: str

    budget: float = Field(ge=0)

    jumlah_orang: int = Field(ge=1)

    jumlah_destinasi: int = Field(default=3, ge=1, le=10)

    latitude: Optional[float] = None

    longitude: Optional[float] = None