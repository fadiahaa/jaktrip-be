from typing import Optional
from pydantic import BaseModel


class PlannerRequest(BaseModel):

    preferensi: str

    budget: float

    jumlah_orang: int

    jumlah_destinasi: int

    latitude: Optional[float] = None

    longitude: Optional[float] = None