from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.auth_repository import AuthRepository
from app.core.security import decode_access_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Token tidak valid"
        )

    user = AuthRepository.get_user_by_id(
        db,
        int(payload["sub"])
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User tidak ditemukan"
        )

    return user