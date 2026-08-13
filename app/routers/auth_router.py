from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.auth import (
   RegisterRequest,
   LoginRequest
   )
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):

    try:

        user = AuthService.register(
            db,
            request.nama,
            request.email,
            request.password
        )

        return {
            "message": "Register berhasil",
            "user": {
                "id": user.id_user,
                "nama": user.nama,
                "email": user.email
            }
        }

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
        
@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    try:

        return AuthService.login(
            db,
            request.email,
            request.password
        )

    except Exception as e:

        raise HTTPException(
            status_code=401,
            detail=str(e)
        )
        
        
@router.get("/me")
def me(
    current_user: User = Depends(get_current_user)
):

    return {
        "id": current_user.id_user,
        "nama": current_user.nama,
        "email": current_user.email
    }