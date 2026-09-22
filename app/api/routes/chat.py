from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.context_service import (
    build_context,
    is_context_available,
)
from app.services.prompt_service import (
    build_prompt,
    build_multi_question_prompt,
)
from app.services.gemini_services import generate_response
from app.services.conversation_service import analyze_message
from app.services.question_service import decompose_question



router = APIRouter()

def build_sources(
    context: dict,
    question: str
) -> list[dict]:
    sources = []
    seen = set()

    question_lower = question.lower()

    is_structure_question = any(
        keyword in question_lower
        for keyword in [
            "unit",
            "seksi",
            "subbagian",
            "struktur",
            "terdapat",
            "di dalam",
        ]
    )

    is_task_question = any(
        keyword in question_lower
        for keyword in [
            "tugas",
            "fungsi",
        ]
    )

    is_parent_question = any(
        keyword in question_lower
        for keyword in [
            "di bawah siapa",
            "bertanggung jawab kepada siapa",
            "dipimpin siapa",
            "siapa yang memimpin",
        ]
    )

    # VECTOR SOURCES
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

    # GRAPH SOURCES
    for item in context.get("graph_context") or []:
        graph = item.get("context", {})

        children = graph.get("children", [])
        tasks = graph.get("tasks", [])
        parents = graph.get("parents", [])

        # STRUCTURE → Pasal 4
        if is_structure_question:
            for child in children:
                if not child.get("regulation"):
                    continue

                source = {
                    "regulation": child.get("regulation"),
                    "pasal": child.get("pasal"),
                    "ayat": child.get("ayat"),
                    "page": child.get("page"),
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

        # TASK / FUNCTION → Pasal 5
        if is_task_question:
            for task in tasks:
                if not task.get("regulation"):
                    continue

                source = {
                    "regulation": task.get("regulation"),
                    "pasal": task.get("pasal"),
                    "ayat": task.get("ayat"),
                    "page": task.get("page"),
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

        # PARENT / RELATION → Pasal 3
        if is_parent_question:
            for parent in parents:
                if not parent.get("regulation"):
                    continue

                source = {
                    "regulation": parent.get("regulation"),
                    "pasal": parent.get("pasal"),
                    "ayat": parent.get("ayat"),
                    "page": parent.get("page"),
                }

                key = (
                    question,
                    source["regulation"],
                    source["pasal"],
                    source["page"],
                )

                if key not in seen:
                    seen.add(key)
                    sources.append(source)

    return sources

def build_multi_question_sources(
    question_results: list[dict]
) -> list[dict]:

    sources = []
    seen = set()

    for item in question_results:
        question = item["question"]
        context = item["context"]

        question_lower = question.lower()

        is_task = any(
            keyword in question_lower
            for keyword in ["tugas", "fungsi"]
        )

        is_leadership = any(
            keyword in question_lower
            for keyword in [
                "siapa yang memimpin",
                "dipimpin siapa",
                "di bawah siapa",
                "bertanggung jawab kepada siapa",
                "memimpin",
            ]
        )

        # ==================================================
        # VECTOR SOURCES
        # ==================================================

        for result in context.get(
            "vector_context",
            []
        ):
            regulation = result.get(
                "regulation_number"
            )

            pasal = result.get("pasal")
            ayat = result.get("ayat")
            page = result.get("page")

            if not regulation:
                continue

            # ----------------------------------------------
            # TASK / FUNCTION
            # ----------------------------------------------
            if is_task:
                if pasal != "Pasal 5":
                    continue

            # ----------------------------------------------
            # LEADERSHIP
            # ----------------------------------------------
            elif is_leadership:
                if pasal != "Pasal 3":
                    continue

            else:
                # Untuk sementara, kalau intent belum
                # dikenali, gunakan hasil vector.
                pass

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
        # GRAPH SOURCES
        # ==================================================

        for graph_item in (
            context.get("graph_context") or []
        ):
            graph = graph_item.get(
                "context",
                {}
            )

            intent = graph_item.get(
                "intent"
            )

            # ----------------------------------------------
            # TASK
            # ----------------------------------------------
            if intent == "task":
                for task in graph.get(
                    "tasks",
                    []
                ):
                    regulation = task.get(
                        "regulation"
                    )

                    if not regulation:
                        continue

                    source = {
                        "question": question,
                        "regulation": regulation,
                        "pasal": task.get("pasal"),
                        "ayat": task.get("ayat"),
                        "page": task.get("page"),
                    }

                    key = (
                        question,
                        source["regulation"],
                        source["pasal"],
                        source["page"],
                    )

                    if key not in seen:
                        seen.add(key)
                        sources.append(source)

            # ----------------------------------------------
            # LEADERSHIP
            # ----------------------------------------------
            elif intent == "leadership":
                for parent in graph.get(
                    "parents",
                    []
                ):
                    regulation = parent.get(
                        "regulation"
                    )

                    if not regulation:
                        continue

                    source = {
                        "question": question,
                        "regulation": regulation,
                        "pasal": parent.get("pasal"),
                        "ayat": parent.get("ayat"),
                        "page": parent.get("page"),
                    }

                    key = (
                        question,
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

    questions = decompose_question(
        conversation.question
    )

    print("DECOMPOSED QUESTIONS:", questions)

    question_results = []

    for question in questions:
        context = build_context(question)

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
        return {
            "answer": (
                "Informasi tersebut tidak ditemukan "
                "dalam basis pengetahuan."
            ),
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

    try:
        answer = generate_response(prompt)
    except RuntimeError as e:
        answer = str(e)

    return {
        "answer": answer,
        "sources": sources
    }