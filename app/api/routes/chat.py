from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.context_service import (
    build_context,
    is_context_available,
)
from app.services.prompt_service import build_prompt
from app.services.gemini_services import generate_response

router = APIRouter()


def build_sources(context: dict) -> list[dict]:
    sources = []
    seen = set()

    for result in context.get("vector_context", []):
        source = {
            "regulation": (
                f"Pergub Aceh No. "
                f"{result.get('regulation_number')} "
                f"Tahun {result.get('year')}"
            ),
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
    context = build_context(request.question)

    if not is_context_available(context):
        return {
            "answer": (
                "Informasi tersebut tidak ditemukan "
                "dalam basis pengetahuan."
            ),
            "sources": []
        }

    prompt = build_prompt(
        request.question,
        context
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