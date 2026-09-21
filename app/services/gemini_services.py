from google import genai
from google.genai import errors

from app.core.config import settings

client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


def generate_response(prompt: str) -> str:
    try:
        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt,
        )

        return interaction.output_text

    except errors.APIError as e:
        if e.code == 429:
            raise RuntimeError(
                "Layanan AI sedang mencapai batas penggunaan. "
                "Silakan coba lagi nanti."
            )

        raise