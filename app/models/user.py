from sqlalchemy import Column, Integer, String, TIMESTAMP, func

from app.database.base import Base


class User(Base):

    __tablename__ = "users"

    id_user = Column(Integer, primary_key=True, index=True)

    nama = Column(String(100))

    email = Column(String(100), unique=True)

    password = Column(String(255))

    created_at = Column(TIMESTAMP, server_default=func.now())

    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )