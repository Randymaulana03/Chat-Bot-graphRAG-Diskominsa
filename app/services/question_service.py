import re


QUESTION_WORDS = (
    "apa",
    "siapa",
    "bagaimana",
    "mengapa",
    "kenapa",
    "kapan",
    "dimana",
    "di mana",
    "berapa",
    "apakah",
)


def normalize_question(question: str) -> str:
    """
    Normalisasi istilah berdasarkan scope knowledge base.
    """

    question = question.strip()

    # Dalam knowledge base saat ini,
    # UPTD merujuk pada UPTD Statistik.
    question = re.sub(
        r"\bUPTD\b(?!\s+Statistik\b)",
        "UPTD Statistik",
        question,
        flags=re.IGNORECASE,
    )

    return question


def _ensure_question_mark(question: str) -> str:
    question = question.strip()

    if not question.endswith("?"):
        question += "?"

    return question

def _normalize_questions(questions: list[str]) -> list[str]:
    result = []

    for question in questions:
        question = question.strip(" ,.;")

        if not question:
            continue

        question = normalize_question(question)

        # Kapitalisasi awal pertanyaan
        question = question[0].upper() + question[1:]

        question = _ensure_question_mark(question)

        result.append(question)

    return result


def _split_explicit_questions(question: str) -> list[str]:
    pattern = re.compile(
        r"(?:^|,\s*|\s+dan\s+juga\s+|\s+dan\s+|\s+serta\s+)"
        r"(?=(?:"
        r"apa|siapa|bagaimana|mengapa|kenapa|"
        r"kapan|dimana|di mana|berapa|apakah"
        r")\b)",
        re.IGNORECASE,
    )

    fragments = pattern.split(question)

    fragments = [
        fragment.strip(" ,.")
        for fragment in fragments
        if fragment.strip(" ,.")
    ]

    if len(fragments) <= 1:
        return []

    for fragment in fragments:
        if not re.match(
            rf"^(?:{'|'.join(QUESTION_WORDS)})\b",
            fragment,
            re.IGNORECASE,
        ):
            return []

    return _normalize_questions(fragments)


def _split_question_sentences(question: str) -> list[str]:
    """
    Memecah pertanyaan yang sudah dipisahkan dengan ? . !
    """

    fragments = re.split(
        r"(?<=[?!.])\s+",
        question,
    )

    fragments = [
        fragment.strip()
        for fragment in fragments
        if fragment.strip()
    ]

    if len(fragments) <= 1:
        return []

    # Pastikan memang lebih dari satu pertanyaan.
    question_fragments = []

    for fragment in fragments:
        if re.match(
            rf"^(?:{'|'.join(QUESTION_WORDS)})\b",
            fragment,
            re.IGNORECASE,
        ):
            question_fragments.append(fragment)

    if len(question_fragments) > 1:
        return _normalize_questions(question_fragments)

    return []


def _split_shared_question(question: str) -> list[str]:
    """
    Menangani pola:

    Apa tugas A dan B?
    Apa tugas A dan juga B?
    Apa fungsi A serta B?
    """

    pattern = re.compile(
        r"^(apa|siapa|bagaimana|mengapa|kenapa|"
        r"kapan|dimana|di mana|berapa|apakah)"
        r"\s+(tugas|fungsi|unit|seksi|subbagian|"
        r"struktur|nama|peran|kedudukan)"
        r"\s+(.+?)"
        r"\s+(?:dan juga|dan|serta|juga)\s+"
        r"(.+?)\??$",
        re.IGNORECASE,
    )

    match = pattern.match(question)

    if not match:
        return []

    question_word = match.group(1)
    context = match.group(2)
    first_target = match.group(3).strip()
    second_target = match.group(4).strip()

    # Kalau target kedua ternyata memulai pertanyaan baru,
    # jangan pecah dengan shared context.
    if re.match(
        rf"^(?:{'|'.join(QUESTION_WORDS)})\b",
        second_target,
        re.IGNORECASE,
    ):
        return []

    return _normalize_questions([
        f"{question_word} {context} {first_target}",
        f"{question_word} {context} {second_target}",
    ])


def decompose_question(question: str) -> list[str]:
    """
    Memecah satu input menjadi beberapa sub-question.

    Tidak menggunakan Gemini.
    """

    question = question.strip()

    if not question:
        return []

    question = normalize_question(question)

    # =========================================================
    # 1. Pertanyaan eksplisit yang dipisahkan koma
    #
    # Apa tugas A, apa fungsi B, dan siapa C?
    # =========================================================

    result = _split_explicit_questions(question)

    if result:
        return result

    # =========================================================
    # 2. Pertanyaan eksplisit yang dipisahkan ? / . / !
    #
    # Apa tugas A? Apa fungsi B?
    # =========================================================

    result = _split_question_sentences(question)

    if result:
        return result

    # =========================================================
    # 3. Pertanyaan dengan shared question context
    #
    # Apa tugas A dan B?
    # Apa fungsi A dan juga B?
    # =========================================================

    result = _split_shared_question(question)

    if result:
        return result

    # =========================================================
    # 4. Tidak bisa dipecah
    # =========================================================

    return [
        normalize_question(question)
    ]