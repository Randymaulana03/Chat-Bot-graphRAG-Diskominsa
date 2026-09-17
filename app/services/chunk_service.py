import re


def chunk_pages(pages: list[dict]) -> list[dict]:
    chunks = []

    current_bab = None
    current_bagian = None
    current_paragraf = None
    current_pasal = None
    current_ayat = None

    current_content = []
    content_page = None

    started_document = False

    def save_chunk():
        nonlocal current_content, content_page

        if not current_content:
            return

        content = " ".join(current_content).strip()

        if not content:
            current_content = []
            content_page = None
            return

        chunks.append({
            "content": content,
            "bab": current_bab,
            "bagian": current_bagian,
            "paragraf": current_paragraf,
            "pasal": current_pasal,
            "ayat": current_ayat,
            "page": content_page
        })

        current_content = []
        content_page = None

    for page in pages:
        page_number = page["page"]
        lines = page["text"].splitlines()

        for line in lines:
            line = line.strip()

            if not line:
                continue

            # =========================
            # BAB
            # =========================
            if re.match(
                r"^BAB\s+[IVXLCDM]+$",
                line,
                re.IGNORECASE
            ):
                save_chunk()

                started_document = True
                current_bab = line
                current_bagian = None
                current_paragraf = None
                current_pasal = None
                current_ayat = None

                continue

            # Abaikan bagian sebelum BAB pertama
            if not started_document:
                continue

            # =========================
            # BAGIAN
            # =========================
            if re.match(
                r"^Bagian\s+\w+",
                line,
                re.IGNORECASE
            ):
                save_chunk()

                current_bagian = line
                current_paragraf = None
                current_pasal = None
                current_ayat = None

                continue

            # =========================
            # PARAGRAF
            # =========================
            if re.match(
                r"^Paragraf\s+\d+",
                line,
                re.IGNORECASE
            ):
                save_chunk()

                current_paragraf = line
                current_pasal = None
                current_ayat = None

                continue

            # =========================
            # PASAL
            # =========================
            if re.match(
                r"^Pasal\s+\d+\s*$",
                line,
                re.IGNORECASE
            ):
                save_chunk()

                current_pasal = line
                current_ayat = None

                continue

            # =========================
            # AYAT
            # =========================
            ayat_match = re.match(
                r"^\((\d+)\)\s*(.*)",
                line
            )

            if ayat_match and current_pasal:
                ayat_number = int(ayat_match.group(1))

                current_ayat_number = None

                if current_ayat:
                    current_ayat_number = int(
                        re.search(
                            r"\d+",
                            current_ayat
                        ).group()
                    )

                is_new_ayat = (
                    current_ayat is None
                    or ayat_number > current_ayat_number
                )

                if is_new_ayat:
                    save_chunk()
                    current_ayat = f"({ayat_number})"

                if content_page is None:
                    content_page = page_number

                current_content.append(line)

                continue

            # =========================
            # KONTEN LANJUTAN
            # =========================
            if current_pasal:
                if content_page is None:
                    content_page = page_number

                current_content.append(line)

    # Simpan chunk terakhir
    save_chunk()

    return chunks


def assign_chunk_ids(
    chunks: list[dict],
    regulation_number: str,
    year: int
) -> list[dict]:

    prefix = f"pergub-{regulation_number}-{year}"

    for index, chunk in enumerate(chunks, start=1):
        chunk["chunk_id"] = (
            f"{prefix}-chunk-{index:03d}"
        )

    return chunks