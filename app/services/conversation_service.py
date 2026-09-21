import re
from dataclasses import dataclass


GREETING_WORDS = [
    "hai",
    "halo",
    "hello",
    "hi",
]


@dataclass
class ConversationResult:
    question: str
    name: str | None
    is_greeting_only: bool
    reply: str | None


def detect_greeting(text: str) -> bool:
    text = text.lower().strip()

    return any(
        text.startswith(word)
        for word in GREETING_WORDS
    )


def extract_name(text: str) -> str | None:
    patterns = [
        r"\bsaya bernama\s+([A-Za-z]+)",
        r"\bnama saya\s+([A-Za-z]+)",
        r"\bsaya\s+([A-Za-z]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(1).strip()

    return None


def analyze_message(text: str) -> ConversationResult:
    greeting = detect_greeting(text)
    name = extract_name(text)

    # Jika hanya greeting / perkenalan tanpa pertanyaan
    if greeting and not _contains_question(text, name):
        if name:
            reply = (
                f"Hai {name}! Senang berkenalan. "
                "Ada yang ingin kamu tanyakan?"
            )
        else:
            reply = (
                "Hai! Saya siap membantu menjawab "
                "pertanyaan seputar Diskominsa Aceh."
            )

        return ConversationResult(
            question="",
            name=name,
            is_greeting_only=True,
            reply=reply,
        )

    # Bersihkan bagian greeting dan nama
    question = _clean_question(text, greeting, name)

    return ConversationResult(
        question=question,
        name=name,
        is_greeting_only=False,
        reply=None,
    )


def _contains_question(
    text: str,
    name: str | None
) -> bool:
    text_lower = text.lower()

    question_words = [
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
        "tugas",
        "fungsi",
    ]

    return any(
        word in text_lower
        for word in question_words
    )


def _clean_question(
    text: str,
    greeting: bool,
    name: str | None
) -> str:
    question = text.strip()

    if greeting:
        question = re.sub(
            r"^(hai|halo|hello|hi)[,!.\s]*",
            "",
            question,
            flags=re.IGNORECASE,
        )

    if name:
        patterns = [
            rf"\bsaya bernama\s+{re.escape(name)}[,!.\s]*",
            rf"\bnama saya\s+{re.escape(name)}[,!.\s]*",
            rf"\bsaya\s+{re.escape(name)}[,!.\s]*",
        ]

        for pattern in patterns:
            question = re.sub(
                pattern,
                "",
                question,
                flags=re.IGNORECASE,
            )

    return question.strip(" ,.!?")