from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.schemas.planner import PlannerRequest

from app.core.dependencies import get_current_user

from app.services.planner_service import PlannerService


router = APIRouter(
    prefix="/planner",
    tags=["Planner"]
)


@router.post("/save")
def save_planner(

    request: PlannerRequest,

    current_user=Depends(get_current_user),

    db: Session = Depends(get_db)

):

    return PlannerService.save(
        db,
        current_user.id_user,
        request
    )
    
@router.get("/history")
def history(

    current_user=Depends(get_current_user),

    db: Session = Depends(get_db)

):

    return PlannerService.history(

        db,

        current_user.id_user

    )
@router.get("/{planner_id}")
def detail(

    planner_id: int,

    current_user=Depends(get_current_user),

    db: Session = Depends(get_db)

):

    return PlannerService.detail(

        db,

        planner_id,

        current_user.id_user

    )
    
@router.delete("/{planner_id}")
def delete(

    planner_id: int,

    current_user=Depends(get_current_user),

    db: Session = Depends(get_db)

):

    return PlannerService.delete(

        db,

        planner_id,

        current_user.id_user

    )