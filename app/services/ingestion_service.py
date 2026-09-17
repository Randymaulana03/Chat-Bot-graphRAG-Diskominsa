from app.services.pdf_service import extract_pdf
from app.services.chunk_service import (
    chunk_pages,
    assign_chunk_ids,
)
from app.services.embedding_service import generate_embedding
from app.services.vector_service import (
    insert_document_chunk,
    get_existing_chunk_ids,
)


def ingest_pdf(
    file_path: str,
    document_id: int,
    regulation_number: str,
    year: int,
) -> dict:

    pages = extract_pdf(file_path)

    chunks = chunk_pages(pages)

    chunks = assign_chunk_ids(
        chunks,
        regulation_number,
        year,
    )

    existing_chunk_ids = get_existing_chunk_ids(
        document_id
    )

    inserted = 0
    skipped = 0

    for chunk in chunks:

        if chunk["chunk_id"] in existing_chunk_ids:
            skipped += 1
            continue

        embedding = generate_embedding(
            chunk["content"]
        )

        insert_document_chunk(
            document_id=document_id,
            chunk=chunk,
            embedding=embedding,
        )

        inserted += 1

    return {
        "total_chunks": len(chunks),
        "inserted": inserted,
        "skipped": skipped,
    }