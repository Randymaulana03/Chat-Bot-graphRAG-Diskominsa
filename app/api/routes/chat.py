from fastapi import APIRouter, HTTPException
from groq import Groq  # 1. Pastikan import Groq ada

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.context_service import (
    build_context,
    is_context_available,
)
from app.services.prompt_service import (
    build_multi_question_prompt,
)
from app.services.gemini_services import generate_response
from app.services.conversation_service import analyze_message
from app.services.question_service import decompose_question_hybrid
from app.core.config import settings




router = APIRouter()
groq_client = Groq(api_key=settings.GROQ_API_KEY)

def build_multi_question_sources(
    question_results: list[dict],
    max_sources_per_question: int = 2
) -> list[dict]:
    sources = []
    seen = set()

    for item in question_results:
        question = item["question"]
        context = item["context"]

        # ==================================================
        # 1. VECTOR SOURCES
        # ==================================================
        # Tampilkan vector context jika vector_relevant True
        # ATAU jika vector_relevant belum di-set eksplisit.
        vector_relevant = context.get("vector_relevant")
        if vector_relevant is not False:
            vector_results = context.get("vector_context", []) or []
        else:
            vector_results = []

        for result in vector_results:
            regulation = result.get("regulation_number")
            pasal = result.get("pasal")
            ayat = result.get("ayat")
            page = result.get("page")

            if not regulation:
                continue

            source = {
                "question": question,
                "regulation": regulation,
                "pasal": pasal,
                "ayat": ayat,
                "page": page,
            }

            key = (
                question,
                regulation,
                pasal,
                ayat,
                page,
            )

            if key not in seen:
                seen.add(key)
                sources.append(source)

        # ==================================================
        # 2. GRAPH SOURCES
        # ==================================================
        for graph_item in (context.get("graph_context") or []):
            print("DEBUG GRAPH ITEM FOR SOURCE:", graph_item)
            graph = graph_item.get("context", {}) or {}
            intent = graph_item.get("intent")

            # Helper internal untuk append source agar DRY
            def _add_graph_source(reg, pas, ay, pg):
                if not reg:
                    return
                src = {
                    "question": question,
                    "regulation": reg,
                    "pasal": pas,
                    "ayat": ay,
                    "page": pg,
                }
                src_key = (
                    question,
                    reg,
                    pas,
                    ay,
                    pg,
                )
                if src_key not in seen:
                    seen.add(src_key)
                    sources.append(src)

            # ----------------------------------------------
            # TASK
            # ----------------------------------------------
            if intent == "task":
                for task in graph.get("tasks", []) or []:
                    _add_graph_source(
                        task.get("regulation"),
                        task.get("pasal"),
                        task.get("ayat"),
                        task.get("page"),
                    )

            # ----------------------------------------------
            # LEADERSHIP
            # ----------------------------------------------
            elif intent == "leadership":
                # Keduanya diperiksa: 'leaders' (dari unit leadership) dan 'parents'
                for leader in graph.get("leaders", []) or []:
                    _add_graph_source(
                        leader.get("regulation"),
                        leader.get("pasal"),
                        leader.get("ayat"),
                        leader.get("page"),
                    )
                for parent in graph.get("parents", []) or []:
                    _add_graph_source(
                        parent.get("regulation"),
                        parent.get("pasal"),
                        parent.get("ayat"),
                        parent.get("page"),
                    )

            # ----------------------------------------------
            # PARENT
            # ----------------------------------------------
            elif intent == "parent":
                for parent in graph.get("parents", []) or []:
                    _add_graph_source(
                        parent.get("regulation"),
                        parent.get("pasal"),
                        parent.get("ayat"),
                        parent.get("page"),
                    )
                for leader in graph.get("leaders", []) or []:
                    _add_graph_source(
                        leader.get("regulation"),
                        leader.get("pasal"),
                        leader.get("ayat"),
                        leader.get("page"),
                    )

            # ----------------------------------------------
            # STRUCTURE
            # ----------------------------------------------
            elif intent == "structure":
                for child in graph.get("children", []) or []:
                    _add_graph_source(
                        child.get("regulation"),
                        child.get("pasal"),
                        child.get("ayat"),
                        child.get("page"),
                    )

            # ----------------------------------------------
            # ORGANIZATION
            # ----------------------------------------------
            elif intent == "organization":
                for leader in graph.get("leaders", []) or []:
                    _add_graph_source(
                        leader.get("regulation"),
                        leader.get("pasal"),
                        leader.get("ayat"),
                        leader.get("page"),
                    )

            # ----------------------------------------------
            # RELATIONSHIP
            # ----------------------------------------------
            elif intent == "relationship":
                for graph_source in graph.get("sources", []) or []:
                    _add_graph_source(
                        graph_source.get("regulation"),
                        None,
                        None,
                        None,
                    )

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

    questions = decompose_question_hybrid(
        conversation.question,
        groq_client=groq_client
    )

    print("DECOMPOSED QUESTIONS:", questions)

    question_results = []

    for question in questions:
        context = build_context(question)
        print("\n" + "=" * 50)
        print("SOURCE INPUT")
        print("=" * 50)

        print("VECTOR CONTEXT:")
        print(context.get("vector_context"))

        print("\nGRAPH CONTEXT:")
        print(context.get("graph_context"))

        question_results.append({
            "question": question,
            "context": context,
        })

    print("QUESTION RESULTS:", question_results)

    has_any_context = any(
        is_context_available(item["context"])
        for item in question_results
    )

    if not has_any_context:
        if conversation.name:
            answer = (
                f"Halo {conversation.name}.\n\n"
                "Informasi tersebut tidak ditemukan "
                "dalam basis pengetahuan."
            )
        else:
            answer = (
                "Informasi tersebut tidak ditemukan "
                "dalam basis pengetahuan."
            )

        return {
            "answer": answer,
            "sources": []
        }

    prompt = build_multi_question_prompt(
        question_results,
        conversation.name
    )

    print("MULTI QUESTION PROMPT:")
    print(prompt)

    sources = build_multi_question_sources(
        question_results
    )

    print("\n" + "=" * 40)
    print("FINAL SOURCES FROM API:")
    print(sources)
    print("=" * 40)

    # 1. Jalankan LLM Synthesizer (Gemini) lebih dulu untuk mendapatkan jawaban
    try:
        answer = generate_response(prompt)
    except RuntimeError as e:
        answer = str(e)

    # 2. Cek apakah jawaban Gemini menyatakan bahwa informasi TIDAK DITEMUKAN
    not_found_keywords = [
        "tidak ditemukan dalam basis pengetahuan",
        "informasi tersebut tidak ditemukan",
        "tidak menemukan informasi",
        "tidak ada informasi"
    ]
    
    is_not_found = any(keyword in answer.lower() for keyword in not_found_keywords)

    # 3. Logika Filter Sumber:
    # Jika jawaban bernilai "tidak ditemukan", PAKSA sources menjadi list kosong []
    if is_not_found:
        sources = []
    else:
        sources = build_multi_question_sources(question_results)

    # 4. Return response ke API
    return {
        "answer": answer,
        "sources": sources
    }