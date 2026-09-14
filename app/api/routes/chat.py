from fastapi import APIRouter
from app.schemas.chat import ChatRequest

router = APIRouter()


@router.post("/api/chat")
def chat(request: ChatRequest):
    return {
        "answer": f"Pertanyaan kamu adalah: {request.question}"
    }