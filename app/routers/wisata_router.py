from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.wisata_service import WisataService

router = APIRouter(
    prefix="/wisata",
    tags=["Wisata"]
)


@router.get("")
def get_all_wisata(
    db: Session = Depends(get_db)
):
    return WisataService.get_all(db)

@router.get("/kategori/{kategori}")
def get_kategori(
    kategori: str,
    db: Session = Depends(get_db)
):

    return WisataService.get_by_kategori(
        db,
        kategori
    )
    
@router.get("/{wisata_id}")
def get_detail_wisata(
    wisata_id: int,
    db: Session = Depends(get_db)
):

    wisata = WisataService.get_detail(
        db,
        wisata_id
    )

    if wisata is None:
        raise HTTPException(
            status_code=404,
            detail="Wisata tidak ditemukan"
        )

    return wisata


