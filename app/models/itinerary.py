from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.sql import func

from app.database.base import Base


class Itinerary(Base):

    __tablename__ = "itinerary"

    id_itinerary = Column(
        Integer,
        primary_key=True,
        index=True
    )

    id_planner = Column(
        Integer,
        ForeignKey("planner.id_planner")
    )

    total_biaya = Column(
        DECIMAL(10, 2)
    )

    sisa_budget = Column(
        DECIMAL(10, 2)
    )

    total_durasi = Column(
        Integer
    )

    total_jarak = Column(
        DECIMAL(10, 2)
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )