def build_prompt(
    question: str,
    context: dict,
) -> str:

    vector_context = context.get(
        "vector_context",
        []
    )

    graph_context = context.get(
        "graph_context"
    )

    vector_text = ""

    for i, result in enumerate(
        vector_context,
        start=1
    ):
        vector_text += f"""
[Vector Result {i}]
Pasal: {result.get("pasal")}
Ayat: {result.get("ayat")}
Halaman: {result.get("page")}
Isi: {result.get("content")}
"""

    graph_text = ""

    if graph_context:
        graph_text = f"""
Entity: {graph_context.get("entity")}

Graph Context:
{graph_context.get("context")}
"""

    prompt = f"""
Kamu adalah chatbot informasi
Dinas Komunikasi, Informatika dan Persandian Aceh.

Jawab pertanyaan pengguna hanya berdasarkan
konteks yang diberikan di bawah ini.

Basis pengetahuan chatbot hanya berasal dari
Peraturan Gubernur Aceh Nomor 119 Tahun 2016
dan Peraturan Gubernur Aceh Nomor 61 Tahun 2020.

Jika informasi yang dibutuhkan tidak ditemukan
dalam konteks, katakan bahwa informasi tersebut
tidak ditemukan dalam basis pengetahuan.

Jangan mengarang informasi.
Jangan menggunakan pengetahuan di luar konteks.

=== VECTOR CONTEXT ===
{vector_text}

=== GRAPH CONTEXT ===
{graph_text}

=== PERTANYAAN PENGGUNA ===
{question}

Jawab dalam bahasa Indonesia dengan jelas dan ringkas.
"""

    return prompt.strip()