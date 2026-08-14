import os
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

# Full DATABASE_URL override if provided (e.g., Neon / Supabase pooled URI)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    port = DB_PORT or 5432
    DATABASE_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{port}/{DB_NAME}"
    )

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

connect_args = {}
if "postgresql" in DATABASE_URL:
    if DB_SSL or any(cloud in DATABASE_URL for cloud in ["neon.tech", "supabase.co", "aivencloud.com"]):
        connect_args["sslmode"] = "require"
elif "mysql" in DATABASE_URL and DB_SSL:
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
