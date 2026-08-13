from sqlalchemy.orm import Session

from app.models.user import User


class AuthRepository:

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email).first()


    @staticmethod
    def create_user(db: Session, user: User):

        db.add(user)
        db.commit()
        db.refresh(user)

        return user
   
    @staticmethod
    def login(db: Session, email: str):
      return db.query(User).filter(
         User.email == email
      ).first()
      
    @staticmethod
    def get_user_by_id(
      db: Session,
      user_id: int
   ):
      return db.query(User).filter(
         User.id_user == user_id
      ).first()