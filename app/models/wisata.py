from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DECIMAL,
    TIME,
    TIMESTAMP,
    func,
    Enum
)

from app.database.base import Base


class Wisata(Base):

    __tablename__ = "wisata"

    id_wisata = Column(Integer, primary_key=True, index=True)

    nama_wisata = Column(String(150))

    kategori = Column(
        Enum(
            "Sejarah",
            "Budaya",
            "Alam",
            "Hiburan",
            "Kuliner",
            "Religi",
            "Edukasi",
            name="wisata_kategori_enum"
        )
    )

    wilayah = Column(
        Enum(
            "Jakarta Pusat",
            "Jakarta Selatan",
            "Jakarta Barat",
            "Jakarta Timur",
            "Jakarta Utara",
            name="wisata_wilayah_enum"
        )
    )

    alamat = Column(Text)

    deskripsi = Column(Text)

    harga_min = Column(DECIMAL(10,2))

    harga_max = Column(DECIMAL(10,2))

    estimasi_durasi = Column(Integer)

    latitude = Column(DECIMAL(10,7))

    longitude = Column(DECIMAL(10,7))

    rating = Column(DECIMAL(2,1))

    link_maps = Column(Text)

    gambar = Column(Text)

    created_at = Column(TIMESTAMP, server_default=func.now())

    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )