from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SSL = os.getenv("DB_SSL", "").lower() in ("1", "true", "yes", "on")
DB_SSL_CA = os.getenv("DB_SSL_CA")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
] or [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]