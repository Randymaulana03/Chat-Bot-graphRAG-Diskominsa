from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        description="Pertanyaan yang ingin diajukan kepada chatbot"
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Question tidak boleh kosong")

        return value


class Source(BaseModel):
    question: str
    regulation: str
    pasal: str | None = None
    ayat: str | None = None
    page: int | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] = []