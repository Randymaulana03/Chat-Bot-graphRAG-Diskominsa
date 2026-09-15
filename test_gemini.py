from app.services.gemini_services import generate_response

result = generate_response(
    "Jawab singkat dalam bahasa Indonesia: apa itu RAG?"
)
print(result)