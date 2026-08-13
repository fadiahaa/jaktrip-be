from sqlalchemy import Column, Integer, ForeignKey, TIME

from app.database.base import Base


class ItineraryDetail(Base):

    __tablename__ = "itinerary_detail"

    id_detail = Column(
        Integer,
        primary_key=True,
        index=True
    )

    id_itinerary = Column(
        Integer,
        ForeignKey("itinerary.id_itinerary")
    )

    id_wisata = Column(
        Integer,
        ForeignKey("wisata.id_wisata")
    )

    urutan = Column(
        Integer
    )

    estimasi_datang = Column(
        TIME,
        nullable=True
    )

    estimasi_selesai = Column(
        TIME,
        nullable=True
    )