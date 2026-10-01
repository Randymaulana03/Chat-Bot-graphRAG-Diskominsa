import json
import re
from groq import Groq, APIError

# RegEx Pattern untuk mendeteksi keberadaan kata rujukan (termasuk persona)
COREFERENCE_PATTERNS = (
    r"(-nya\b|\bnya\b|\bdia\b|\bbeliau\b|\bia\b|\btersebut\b|\byang memimpin\b|\bpimpinannya\b)"
)

KNOWN_ENTITIES = [
    # Organization
    "Dinas Komunikasi, Informatika dan Persandian Aceh",
    # Units (Bidang / UPTD / Sekretariat)
    "Bidang Layanan E-Government",
    "Bidang Pengelolaan Komunikasi Publik",
    "Bidang Pengelolaan dan Layanan Informasi Publik",
    "Bidang Persandian",
    "Bidang Teknologi Informasi dan Komunikasi",
    "Kelompok Jabatan Fungsional UPTD Statistik",
    "Kelompok Jabatan Fungsional",
    "Sekretariat",
    "UPTD Statistik",
    # Seksi
    "Seksi Geospasial",
    "Seksi Hubungan Media",
    "Seksi Infrastruktur dan Teknologi",
    "Seksi Keamanan Informasi E-Government",
    "Seksi Layanan Informasi Publik",
    "Seksi Operasional Pengamanan Persandian",
    "Seksi Pengawasan dan Evaluasi Penyelenggaraan Persandian",
    "Seksi Pengelolaan Data dan Integrasi Sistem Informasi",
    "Seksi Pengelolaan Informasi Publik",
    "Seksi Pengelolaan Media Komunikasi Publik",
    "Seksi Pengelolaan Opini Publik",
    "Seksi Pengembangan Aplikasi",
    "Seksi Pengembangan Ekosistem E-Government",
    "Seksi Statistik Sektoral",
    "Seksi Sumber Daya Komunikasi Publik",
    "Seksi Tata Kelola E-Government",
    "Seksi Tata Kelola Persandian",
    # Subbagian
    "Subbagian Hukum, Kepegawaian dan Umum",
    "Subbagian Keuangan dan Pengelolaan Aset",
    "Subbagian Program, Informasi dan Hubungan Masyarakat",
    "Subbagian Tata Usaha",
    # Jabatan
    "Kepala Bidang Layanan E-Government",
    "Kepala Bidang Pengelolaan Komunikasi Publik",
    "Kepala Bidang Pengelolaan dan Layanan Informasi Publik",
    "Kepala Bidang Persandian",
    "Kepala Bidang Teknologi Informasi dan Komunikasi",
    "Kepala Seksi Infrastruktur dan Teknologi",
    "Kepala UPTD Statistik",
    "Kepala Dinas",
    "Kepala UPTD",
    "Sekretaris",
]

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

DECOMPOSER_SYSTEM_PROMPT = """
Kamu adalah modul Query Decomposition untuk RAG Dinas Komunikasi, Informatika dan Persandian Aceh.

Tugasmu:
1. Memecah pertanyaan pengguna yang kompleks, multi-intent, atau informal/gaul menjadi sub-pertanyaan mandiri (standalone) yang formal.
2. Buang semua sapaan, basa-basi, preambul, atau slang (contoh: "hai min", "mau tanya dong", "terima kasih", "permisi admin").
3. Lakukan normalisasi nama/istilah entitas:
   - "UPTD" -> "UPTD Statistik"
   - "TIK" -> "Bidang Teknologi Informasi dan Komunikasi"
   - "Persandian" -> "Bidang Persandian"
4. Setiap pertanyaan HARUS menggunakan bahasa Indonesia yang formal, diawali kata tanya baku (seperti "Apakah", "Apa", "Siapa"), dan diakhiri tanda tanya.
5. Kembalikan HANYA format JSON valid dengan kunci "sub_questions" yang berisi array string pertanyaan.

Contoh Input: "min mau tanya dong tugas UPTD Statistik apaan aja ya? trus klo bidang TIK ngurus apa?"
Contoh Output JSON:
{
  "sub_questions": [
    "Apakah tugas dari UPTD Statistik?",
    "Apakah tugas dari Bidang Teknologi Informasi dan Komunikasi?"
  ]
}
"""


def normalize_question(question: str) -> str:
    question = question.strip()

    # Normalisasi Alias / Singkatan ke Entitas Resmi
    question = re.sub(
        r"\bUPTD\b(?!\s+Statistik\b)",
        "UPTD Statistik",
        question,
        flags=re.IGNORECASE,
    )

    question = re.sub(
        r"\bTIK\b(?!\s+Pemerintah\b)",
        "Bidang Teknologi Informasi dan Komunikasi",
        question,
        flags=re.IGNORECASE,
    )

    question = re.sub(
        r"\be-gov\b|\be-government\b",
        "E-Government",
        question,
        flags=re.IGNORECASE,
    )

    return question


def _ensure_question_mark(question: str) -> str:
    question = question.strip().rstrip("!.")
    if not question.endswith("?"):
        question += "?"
    return question


def _normalize_questions(questions: list[str]) -> list[str]:
    result = []
    for question in questions:
        cleaned_spaces = re.sub(r"\s+", " ", question).strip(" ,.;")
        if not cleaned_spaces:
            continue

        normalized = normalize_question(cleaned_spaces)
        capitalized = normalized[0].upper() + normalized[1:]
        result.append(_ensure_question_mark(capitalized))

    return result


def _clean_preamble(question: str) -> str:
    pattern = re.compile(
        r"^(?:hai|hello|halo|permisi)?\s*"
        r"(?:saya\s+[a-z0-9_-]+\s*,\s*)?"
        r"(?:saya\s+ingin\s+bertanya\s*,\s*|mau\s+tanya\s*,\s*)?",
        re.IGNORECASE,
    )
    cleaned = pattern.sub("", question).strip()
    return cleaned if cleaned else question


def resolve_question_context(questions: list[str]) -> list[str]:
    if len(questions) <= 1:
        return questions

    resolved_questions = []
    first_question = questions[0]

    # 1. Cari Entitas Terpanjang dari KNOWN_ENTITIES pada pertanyaan pertama
    sorted_entities = sorted(KNOWN_ENTITIES, key=len, reverse=True)
    previous_entity = None

    for entity in sorted_entities:
        if re.search(r"\b" + re.escape(entity) + r"\b", first_question, re.IGNORECASE):
            previous_entity = entity
            break

    if not previous_entity:
        entity_match = re.search(
            r"\b((?:UPTD|Bidang|Seksi|Subbagian|Sekretariat)\s+[A-Za-z0-9\s]+?)(?=\s+(?:yang|adalah|merupakan|\?|!|$))",
            first_question,
            re.IGNORECASE,
        )
        if entity_match:
            previous_entity = entity_match.group(1).strip()

    # 2. Pola Rujukan Kata Ganti (Daftar Diperluas)
    reference_patterns = [
        "hubungannya",
        "kaitannya",
        "relasinya",
        "tersebut",
        "yang memimpinnya",
        "yang memimpin",
        "memimpinnya",
        "dipimpin siapa",
        "berada di bawah siapa",
        "tugasnya",
        "fungsinya",
        "kedudukannya",
        "strukturnya",
        "perannya",
        "dia",
        "beliau",
        "ia",
    ]

    # Cek apakah pertanyaan pertama menanyakan sosok Pimpinan/Jabatan
    is_asking_leadership = any(
        kw in first_question.lower()
        for kw in ["siapa yang memimpin", "dipimpin oleh siapa", "siapa pimpinan", "siapa kepala", "siapa pemimpin"]
    )

    for index, question in enumerate(questions):
        if index == 0 or not previous_entity:
            resolved_questions.append(question)
            continue

        question_lower = question.lower()
        has_reference = any(
            re.search(r"\b" + re.escape(pat) + r"\b", question_lower)
            for pat in reference_patterns
        )

        if has_reference and not re.search(
            re.escape(previous_entity), question, re.IGNORECASE
        ):
            # Tentukan entitas Unit (contoh: "UPTD Statistik")
            unit_entity = re.sub(
                r"^(?:Kepala|Sekretaris)\s+",
                "",
                previous_entity,
                flags=re.IGNORECASE,
            ).strip()

            # Tentukan entitas Jabatan/Position (contoh: "Kepala UPTD Statistik")
            if previous_entity.lower().startswith(("kepala", "sekretaris")):
                position_entity = previous_entity
            elif unit_entity.lower().startswith("uptd"):
                position_entity = f"Kepala {unit_entity}"
            elif unit_entity.lower().startswith("bidang"):
                position_entity = f"Kepala {unit_entity}"
            elif unit_entity.lower().startswith("seksi"):
                position_entity = f"Kepala {unit_entity}"
            else:
                position_entity = f"Kepala {unit_entity}"

            # Logika Cerdas: Pilih entitas mana yang dijadikan pengganti kata ganti
            # Jika pertanyaan pertama menanyakan PIMPINAN, maka kata "dia/beliau/tugasnya" merujuk ke JABATAN
            target_entity_for_person = position_entity if is_asking_leadership else unit_entity

            replacements = [
                (r"\bhubungannya\b", f"hubungan {unit_entity}"),
                (r"\bkaitannya\b", f"kaitan {unit_entity}"),
                (r"\brelasinya\b", f"relasi {unit_entity}"),
                (r"\btersebut\b", previous_entity),
                (r"\byang\s*memimpinnya\b", f"yang memimpin {unit_entity}"),
                (r"\bmemimpinnya\b", f"memimpin {unit_entity}"),
                (r"\bdipimpin siapa\b", f"dipimpin oleh siapa {unit_entity}"),
                (r"\bberada di bawah siapa\b", f"berada di bawah siapa {unit_entity}"),
                # Penggantian kata ganti persona ("dia", "beliau", "ia")
                (r"\b(dia|beliau|ia)\b", target_entity_for_person),
                # Penggantian kata rujukan tugas/fungsi
                (r"\btugasnya\b", f"tugas {target_entity_for_person}"),
                (r"\bfungsinya\b", f"fungsi {target_entity_for_person}"),
                (r"\bstrukturnya\b", f"struktur {unit_entity}"),
                (r"\bkedudukannya\b", f"kedudukan {unit_entity}"),
                (r"\bperannya\b", f"peran {unit_entity}"),
            ]

            for pattern, replacement in replacements:
                question = re.sub(pattern, replacement, question, flags=re.IGNORECASE)

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
    pattern = re.compile(
        r"^(apa|siapa|bagaimana|mengapa|kenapa|"
        r"kapan|dimana|di mana|berapa|apakah)"
        r"\s+(tugas|fungsi|unit|seksi|subbagian|"
        r"struktur|nama|peran|kedudukan)"
        r"\s+(?:dari\s+|pada\s+)?"
        r"(.+?)"
        r"\s+(?:dan juga|dan|serta|juga)\s+"
        r"(.+?)\??$",
        re.IGNORECASE,
    )

    match = pattern.match(question)

    if not match:
        return []

    question_word = match.group(1).strip()
    context = match.group(2).strip()
    first_target = match.group(3).strip()
    second_target = match.group(4).strip()

    entity_prefixes = (
        "bidang ",
        "uptd ",
        "seksi ",
        "subbagian ",
        "sekretariat",
        "kelompok ",
        "tik",
        "persandian",
    )

    second_target_lower = second_target.lower()

    is_new_entity = second_target_lower.startswith(entity_prefixes)

    if not is_new_entity:
        return []

    if re.match(
        rf"^(?:{'|'.join(QUESTION_WORDS)})\b",
        second_target,
        re.IGNORECASE,
    ):
        return []

    first_target = re.sub(r"^(?:dari|pada)\s+", "", first_target, flags=re.IGNORECASE)
    second_target = re.sub(r"^(?:dari|pada)\s+", "", second_target, flags=re.IGNORECASE)

    q1 = f"{question_word} {context} dari {first_target}"
    q2 = f"{question_word} {context} dari {second_target}"

    return _normalize_questions([q1, q2])


def _decompose_with_groq(question: str, client: Groq) -> list[str]:
    """
    Fallback LLM Decomposer menggunakan Groq API.
    """
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": DECOMPOSER_SYSTEM_PROMPT},
                {"role": "user", "content": f"Input pengguna: {question}"},
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        sub_questions = data.get("sub_questions", [])

        if sub_questions:
            return _normalize_questions(sub_questions)

    except (APIError, Exception) as e:
        print(f"[WARNING] Groq Decomposer error/fallback: {e}")

    return [_ensure_question_mark(normalize_question(question))]


def decompose_question_hybrid(question: str, groq_client: Groq = None) -> list[str]:
    """
    Entry point Hybrid Decomposer:
    1. Coba RegEx (Fast Path - 0 ms)
    2. Fallback ke Groq LLM (Smart Path - ~100 ms)
    """
    question = question.strip()
    if not question:
        return []

    clean_q = _clean_preamble(question)
    normalized_q = normalize_question(clean_q)

    # 1. FAST PATH: RegEx
    result = _split_explicit_questions(normalized_q)
    if result:
        print("[DECOMPOSER] Used: RegEx Explicit Split")
        return resolve_question_context(result)

    result = _split_question_sentences(normalized_q)
    if result:
        print("[DECOMPOSER] Used: RegEx Sentence Split")
        return resolve_question_context(result)

    result = _split_shared_question(normalized_q)
    if result:
        print("[DECOMPOSER] Used: RegEx Shared Split")
        return resolve_question_context(result)

    # 2. SMART PATH: Groq LLM
    if groq_client:
        print("[DECOMPOSER] Used: Groq LLM Fallback")
        sub_qs = _decompose_with_groq(clean_q, groq_client)
        return resolve_question_context(sub_qs)

    return [_ensure_question_mark(normalized_q)]


def decompose_question(question: str) -> list[str]:
    """
    Backward compatibility wrapper untuk fungsi lama / unit test.
    """
    return decompose_question_hybrid(question)