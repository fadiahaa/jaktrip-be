from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.auth_repository import AuthRepository
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)


class AuthService:

    @staticmethod
    def register(db: Session, nama: str, email: str, password: str):

        existing = AuthRepository.get_user_by_email(db, email)

        if existing:
            raise Exception("Email sudah digunakan")

        user = User(
            nama=nama,
            email=email,
            password=hash_password(password)
        )

        return AuthRepository.create_user(db, user)
     
    @staticmethod
    def login(db: Session, email: str, password: str):

      user = AuthRepository.login(db, email)

      if not user:
         raise Exception("Email tidak ditemukan")

      if not verify_password(password, user.password):
         raise Exception("Password salah")

      token = create_access_token(
         {
               "sub": str(user.id_user)
         }
      )

      return {
         "access_token": token,
         "token_type": "bearer",
         "user": {
               "id": user.id_user,
               "nama": user.nama,
               "email": user.email
         }
      }
     