from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, Text, TIMESTAMP
from sqlalchemy.sql import func

from app.database.base import Base


class Planner(Base):

    __tablename__ = "planner"
    id_planner = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user"))
    preferensi = Column(Text)
    budget = Column(DECIMAL(10, 2))
    jumlah_orang = Column(Integer)
    jumlah_destinasi = Column(Integer)
    latitude = Column(DECIMAL(10, 7), nullable=True)
    longitude = Column(DECIMAL(10, 7), nullable=True)
    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )