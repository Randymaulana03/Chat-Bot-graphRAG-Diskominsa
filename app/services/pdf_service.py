import re

from pypdf import PdfReader


def clean_pdf_text(text: str) -> str:
    # Hapus nomor halaman yang berdiri sendiri
    text = re.sub(
        r"^\s*\d+\s*$",
        "",
        text,
        flags=re.MULTILINE
    )

    # Hapus nomor halaman format -1-, -2-, dst.
    text = re.sub(
        r"^\s*-\d+-\s*$",
        "",
        text,
        flags=re.MULTILINE
    )

    # Hapus baris teks yang terpotong dengan tanda "..."
    text = re.sub(
        r"^\s*\(\d+\).*?\.\.\.\s*$",
        "",
        text,
        flags=re.MULTILINE
    )

    # Rapikan spasi di akhir baris
    text = re.sub(r"[ \t]+", " ", text)

    # Rapikan baris kosong berlebihan
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


def extract_pdf(file_path: str) -> list[dict]:
    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""

        cleaned_text = clean_pdf_text(raw_text)

        pages.append({
            "page": page_number,
            "text": cleaned_text
        })

    return pages