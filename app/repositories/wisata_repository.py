from sqlalchemy.orm import Session

from app.models.wisata import Wisata


class WisataRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(Wisata).all()


    @staticmethod
    def get_by_id(
        db: Session,
        wisata_id: int
    ):
        return db.query(Wisata).filter(
            Wisata.id_wisata == wisata_id
        ).first()


    @staticmethod
    def get_by_kategori(
        db: Session,
        kategori: str
    ):
        return db.query(Wisata).filter(
            Wisata.kategori == kategori
        ).all()