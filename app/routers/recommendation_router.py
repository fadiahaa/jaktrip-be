from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.recommendation import RecommendationRequest
from app.services.recommendation_service import RecommendationService

router = APIRouter(
    prefix="/recommend",
    tags=["Recommendation"]
)


@router.post("")
def recommend(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):

    return RecommendationService.recommend(
        db,
        request
    )