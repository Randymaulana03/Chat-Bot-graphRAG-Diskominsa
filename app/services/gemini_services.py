from google import genai
from google.genai import errors

from app.core.config import settings


client = genai.Client(
    api_key=settings.GEMINI_API_KEY,
    http_options={
        "api_version": "v1"
    }
)


def generate_response(prompt: str) -> str:
    try:
        interaction = client.interactions.create(
            # model="gemini-3.8-flash",
            # model="gemini-3.6-flash",
            model="gemini-3.1-flash-lite",

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

# from groq import APIError, Groq

# from app.core.config import settings

# # Groq SDK otomatis mengarahkan ke endpoint API yang benar
# client = Groq(
#     api_key=settings.GROQ_API_KEY,
# )


# def generate_response(prompt: str) -> str:
#     try:
#         response = client.chat.completions.create(
#             model="openai/gpt-oss-120b",
#             messages=[
#                 {"role": "user", "content": prompt},
#             ],
#             temperature=0.1,
#         )

#         return response.choices[0].message.content

#     except APIError as e:
#         if e.status_code == 429:
#             raise RuntimeError(
#                 "Layanan AI sedang mencapai batas penggunaan. "
#                 "Silakan coba lagi nanti."
#             ) from e

#         raise