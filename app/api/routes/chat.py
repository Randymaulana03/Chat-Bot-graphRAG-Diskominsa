from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.context_service import (
    build_context,
    is_context_available,
)
from app.services.prompt_service import build_prompt
from app.services.gemini_services import generate_response
from app.services.conversation_service import analyze_message

router = APIRouter()


def build_sources(context: dict) -> list[dict]:
    sources = []
    seen = set()

    for result in context.get("vector_context", [])[:3]:
        source = {
            "regulation": result.get("regulation_number"),
            "pasal": result.get("pasal"),
            "ayat": result.get("ayat"),
            "page": result.get("page"),
        }

        key = (
            source["regulation"],
            source["pasal"],
            source["ayat"],
            source["page"],
        )

        if key not in seen:
            seen.add(key)
            sources.append(source)

    return sources


@router.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    message = request.question.strip()

    conversation = analyze_message(message)

    if conversation.is_greeting_only:
        return {
            "answer": conversation.reply,
            "sources": []
        }

    context = build_context(
        conversation.question
    )

    if not is_context_available(context):
        return {
            "answer": (
                "Informasi tersebut tidak ditemukan "
                "dalam basis pengetahuan."
            ),
            "sources": []
        }

    prompt = build_prompt(
        conversation.question,
        context,
        conversation.name
    )

    try:
        answer = generate_response(prompt)

    except RuntimeError as e:
        raise HTTPException(
            status_code=429,
            detail=str(e)
        )

    sources = build_sources(context)

    return {
        "answer": answer,
        "sources": sources
    }