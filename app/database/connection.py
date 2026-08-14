from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
    DB_SSL,
    DB_SSL_CA,
)

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

connect_args = {}
if DB_SSL:
    import certifi

    connect_args = {
        "ssl_ca": DB_SSL_CA or certifi.where(),
        "ssl_verify_cert": True,
        "ssl_verify_identity": True,
    }

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)
