import re

from app.services.embedding_service import generate_embedding
from app.services.vector_service import search_similar_chunks
from app.services.graph_service import (
    retrieve_graph_context,
)


def build_context(question: str) -> dict:
    embedding = generate_embedding(question)

    vector_results = search_similar_chunks(
        embedding,
        limit=5
    )

    graph_result = retrieve_graph_context(question)

    vector_context = vector_results

    # Untuk pertanyaan yang secara eksplisit meminta unit
    # yang berada di bawah suatu unit, gunakan struktur graph
    # sebagai sumber struktur. Vector result struktur dapat
    # mencampur jabatan/kelompok jabatan dengan unit.
    unit_below_question = bool(
        re.search(
            r"\bunit(?:\s+yang)?\s+berada\s+di\s+bawah\b",
            question,
            flags=re.IGNORECASE,
        )
    )

    if unit_below_question and graph_result:
        vector_context = []

    return {
        "question": question,
        "vector_context": vector_context,
        "graph_context": graph_result,
    }


def is_context_available(context: dict) -> bool:
    vector_context = context.get("vector_context") or []
    graph_context = context.get("graph_context") or []

    return bool(vector_context or graph_context)