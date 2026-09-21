from supabase import create_client
from app.core.config import settings

supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_KEY
)

SIMILARITY_THRESHOLD = 0.82


def search_similar_chunks(
    embedding: list[float],
    limit: int = 5
):
    result = supabase.rpc(
        "match_document_chunks",
        {
            "query_embedding": embedding,
            "match_count": limit
        }
    ).execute()

    return result.data


def has_relevant_context(results: list[dict]) -> bool:
    if not results:
        return False

    top_similarity = results[0].get("similarity", 0)

    return top_similarity >= SIMILARITY_THRESHOLD


def insert_document_chunk(
    document_id: int,
    chunk: dict,
    embedding: list[float]
):
    data = {
        "document_id": document_id,
        "content": chunk["content"],
        "chunk_id": chunk["chunk_id"],
        "bab": chunk["bab"],
        "bagian": chunk["bagian"],
        "paragraf": chunk["paragraf"],
        "pasal": chunk["pasal"],
        "ayat": chunk["ayat"],
        "page": chunk["page"],
        "embedding": embedding,
    }

    result = (
        supabase
        .table("document_chunks")
        .insert(data)
        .execute()
    )

    return result.data


def get_existing_chunk_ids(document_id: int) -> set[str]:
    result = (
        supabase
        .table("document_chunks")
        .select("chunk_id")
        .eq("document_id", document_id)
        .execute()
    )

    return {
        row["chunk_id"]
        for row in result.data
    }