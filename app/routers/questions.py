from fastapi import APIRouter
from pydantic import BaseModel
from app.ai_service import generate_important_questions

router = APIRouter()


class QuestionsRequest(BaseModel):
    document_text: str


@router.post("/questions")
async def important_questions(request: QuestionsRequest):

    result = generate_important_questions(
        request.document_text
    )

    return {
        "questions": result
    }