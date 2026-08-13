from pydantic import BaseModel


class WisataResponse(BaseModel):

    id_wisata: int

    nama_wisata: str

    kategori: str

    wilayah: str

    alamat: str

    deskripsi: str

    harga_min: float

    harga_max: float

    estimasi_durasi: int

    latitude: float

    longitude: float

    rating: float | None = None

    link_maps: str

    gambar: str | None = None

    class Config:
        from_attributes = True