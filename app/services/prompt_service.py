def build_prompt(question: str, context: dict) -> str:
    vector_context = context.get("vector_context", [])
    graph_context = context.get("graph_context")

    vector_text = ""

    for i, result in enumerate(vector_context, start=1):
        vector_text += f"""
[Vector Result {i}]
Pasal: {result.get("pasal")}
Ayat: {result.get("ayat")}
Halaman: {result.get("page")}
Isi: {result.get("content")}
"""

    graph_text = ""

    if graph_context:
        for i, item in enumerate(graph_context, start=1):
            entity = item.get("entity")
            graph = item.get("context", {})

            graph_text += f"""
[Graph Entity {i}]
Entity: {entity}

Organisasi:
{graph.get("organizations", [])}

Parent Unit:
{graph.get("parent_units", [])}

Parent Position:
{graph.get("parents", [])}

Unit di dalam:
{graph.get("children", [])}

Tugas:
{graph.get("tasks", [])}
"""

    prompt = f"""
Kamu adalah chatbot informasi
Dinas Komunikasi, Informatika dan Persandian Aceh.

Jawab pertanyaan pengguna hanya berdasarkan konteks
yang diberikan di bawah ini.

Basis pengetahuan chatbot hanya berasal dari:
1. Peraturan Gubernur Aceh Nomor 119 Tahun 2016
2. Peraturan Gubernur Aceh Nomor 61 Tahun 2020

ATURAN JAWABAN:

1. Jawab langsung sesuai pertanyaan pengguna.
2. Gunakan hanya informasi yang terdapat dalam konteks.
3. Jangan menggunakan pengetahuan di luar konteks.
4. Jangan mengarang informasi.
5. Jangan menambahkan informasi yang tidak diperlukan
   untuk menjawab pertanyaan.
6. Jika pertanyaan meminta beberapa informasi,
   jawab semua bagian yang diminta.
7. Jika informasi yang dibutuhkan tidak ditemukan
   dalam konteks, katakan bahwa informasi tersebut
   tidak ditemukan dalam basis pengetahuan.
8. Gunakan bahasa Indonesia yang jelas, ringkas,
   dan mudah dipahami.
9. Jangan menyebutkan "Vector Context", "Graph Context",
   atau proses internal sistem kepada pengguna.

=== VECTOR CONTEXT ===
{vector_text}

=== GRAPH CONTEXT ===
{graph_text}

=== PERTANYAAN PENGGUNA ===
{question}

Berikan jawaban yang langsung menjawab pertanyaan.
"""

    return prompt.strip()