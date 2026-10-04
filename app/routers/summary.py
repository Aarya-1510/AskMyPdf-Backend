from fastapi import APIRouter
from pydantic import BaseModel
from app.ai_service import generate_summary

router = APIRouter()


class SummaryRequest(BaseModel):
    document_text: str


@router.post("/summary")
async def summary(request: SummaryRequest):

    result = generate_summary(request.document_text)

    return {
        "summary": result
    }