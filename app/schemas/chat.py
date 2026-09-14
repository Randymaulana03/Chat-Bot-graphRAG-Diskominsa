from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        description="Pertanyaan yang ingin diajukan ke Chat Bot.",
    )
    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Pertanyaan tidak boleh kosong.")
        return value


class ChatResponse(BaseModel):
    answer: str