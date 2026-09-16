from supabase import create_client

from app.core.config import settings


supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_KEY
)


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