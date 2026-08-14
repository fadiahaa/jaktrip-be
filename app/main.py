import os
from fastapi import FastAPI
from sqlalchemy import text

from app.database.connection import engine
from app.core.config import CORS_ORIGINS
from app.routers.auth_router import router as auth_router
from app.routers.wisata_router import router as wisata_router
from app.routers.recommendation_router import router as recommendation_router
from app.routers.planner_router import router as planner_router
from app.routers.chat_router import router as chat_router

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
app = FastAPI(
    title="JakTrip Planner API",
    version="1.0.0"
)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(wisata_router)
app.include_router(recommendation_router)
app.include_router(planner_router)
app.include_router(chat_router)

@app.get("/")
def root():

    with engine.connect() as conn:

        result = conn.execute(
            text("SELECT COUNT(*) FROM wisata")
        )

        total = result.scalar()

    return {
        "status": "success",
        "message": "Backend Connected",
        "total_wisata": total
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        workers=int(os.getenv("WEB_CONCURRENCY", "1")),
    )