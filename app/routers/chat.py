from fastapi import APIRouter
from pydantic import BaseModel

from app.ai_service import ask_ai


router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    document_text: str


@router.post("/chat")
async def chat(request: ChatRequest):

    result = ask_ai(
        request.question,
        request.document_text
    )

    return {
        "question": request.question,
        "answer": result["answer"],
        "source_type": result["source_type"],
        "sources": result["sources"]
    }