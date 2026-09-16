from google import genai
from app.core.config import settings

client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)

def generate_embedding(text: str) -> list[float]:
    result = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text,
        config={
            "output_dimensionality": 768,
        }
    )

    return result.embeddings[0].values