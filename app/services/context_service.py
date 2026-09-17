from app.services.embedding_service import generate_embedding
from app.services.vector_service import search_similar_chunks
from app.services.graph_service import retrieve_graph_context


def build_context(question: str) -> dict:
    # Vector retrieval
    embedding = generate_embedding(question)

    vector_results = search_similar_chunks(
        embedding,
        limit=5
    )

    # Graph retrieval
    graph_result = retrieve_graph_context(question)

    return {
        "question": question,
        "vector_context": vector_results,
        "graph_context": graph_result,
    }