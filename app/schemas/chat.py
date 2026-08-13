from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str

    budget: Optional[int] = None

    jumlah_orang: Optional[int] = None

    jumlah_destinasi: Optional[int] = 3

    latitude: Optional[float] = None

    longitude: Optional[float] = None