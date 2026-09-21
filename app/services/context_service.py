from app.services.embedding_service import generate_embedding
from app.services.vector_service import (
    search_similar_chunks,
    has_relevant_context,
)
from app.services.graph_service import (
    retrieve_graph_context,
    is_graph_context_relevant,
)


def build_context(question: str) -> dict:
    embedding = generate_embedding(question)

    vector_results = search_similar_chunks(
        embedding,
        limit=5
    )

    vector_relevant = has_relevant_context(vector_results)

    graph_result = retrieve_graph_context(question)

    graph_relevant = is_graph_context_relevant(
        question,
        graph_result
    )

    if not graph_relevant:
        graph_result = None

    return {
        "question": question,
        "vector_context": vector_results if vector_relevant else [],
        "graph_context": graph_result,
        "vector_relevant": vector_relevant,
        "graph_relevant": graph_relevant,
    }

def is_context_available(context: dict) -> bool:
    return (
        context.get("vector_relevant", False)
        or context.get("graph_relevant", False)
    )