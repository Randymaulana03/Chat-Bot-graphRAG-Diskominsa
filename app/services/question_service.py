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

def resolve_question_context(
    questions: list[str]
) -> list[str]:
    """
    Menyelesaikan referensi antar-subquestion.

    Contoh:
    Q1: Apa tugas UPTD Statistik?
    Q2: Apa hubungannya dengan Diskominsa?

    Menjadi:
    Q1: Apa tugas UPTD Statistik?
    Q2: Apa hubungan UPTD Statistik dengan Diskominsa?
    """

    if len(questions) <= 1:
        return questions

    resolved_questions = []

    # Ambil entity dari pertanyaan pertama.
    first_question = questions[0]

    entity_match = re.search(
        r"\bUPTD Statistik\b",
        first_question,
        re.IGNORECASE,
    )

    previous_entity = (
        entity_match.group(0)
        if entity_match
        else None
    )

    for index, question in enumerate(questions):
        if index == 0 or not previous_entity:
            resolved_questions.append(question)
            continue

        question_lower = question.lower()

        reference_patterns = [
            "hubungannya",
            "hubungannya dengan",
            "kaitannya",
            "kaitannya dengan",
            "relasinya",
            "relasinya dengan",
            "tersebut",
        ]

        has_reference = any(
            pattern in question_lower
            for pattern in reference_patterns
        )

        if has_reference and not re.search(
            r"\bUPTD Statistik\b",
            question,
            re.IGNORECASE,
        ):
            question = re.sub(
                r"\bhubungannya\b",
                f"hubungan {previous_entity}",
                question,
                flags=re.IGNORECASE,
            )

            question = re.sub(
                r"\bkaitannya\b",
                f"kaitan {previous_entity}",
                question,
                flags=re.IGNORECASE,
            )

            question = re.sub(
                r"\brelasinya\b",
                f"relasi {previous_entity}",
                question,
                flags=re.IGNORECASE,
            )

            question = re.sub(
                r"\btersebut\b",
                previous_entity,
                question,
                flags=re.IGNORECASE,
            )

        resolved_questions.append(question)

    return _normalize_questions(resolved_questions)

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

    question = question.strip()

    if not question:
        return []

    question = normalize_question(question)

    result = _split_explicit_questions(question)

    if result:
        return resolve_question_context(result)

    result = _split_question_sentences(question)

    if result:
        return resolve_question_context(result)

    result = _split_shared_question(question)

    if result:
        return resolve_question_context(result)

    return [
        normalize_question(question)
    ]