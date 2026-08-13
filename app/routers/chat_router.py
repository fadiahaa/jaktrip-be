from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.schemas.chat import ChatRequest

from app.services.chat_service import ChatService


router = APIRouter(
    prefix="/chat",
    tags=["Chatbot"]
)


@router.post("/")
def chat(

    request: ChatRequest,

    db: Session = Depends(get_db)

):

    return ChatService.chat(

        db,

        request

    )