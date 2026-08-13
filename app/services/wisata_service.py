from sqlalchemy.orm import Session

from app.repositories.wisata_repository import WisataRepository


class WisataService:

    @staticmethod
    def get_all(db: Session):
        return WisataRepository.get_all(db)


    @staticmethod
    def get_detail(
        db: Session,
        wisata_id: int
    ):
        return WisataRepository.get_by_id(
            db,
            wisata_id
        )


    @staticmethod
    def get_by_kategori(
        db: Session,
        kategori: str
    ):
        return WisataRepository.get_by_kategori(
            db,
            kategori
        )