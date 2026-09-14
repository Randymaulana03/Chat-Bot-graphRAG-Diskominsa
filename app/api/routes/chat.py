from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return {
        "answer": f"Pertanyaan kamu adalah: {request.question}"
    }