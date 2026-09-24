def build_prompt(
    question: str,
    context: dict,
    name: str | None = None
) -> str:

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
            intent = item.get("intent")

            tasks = graph.get("tasks", [])
            children = graph.get("children", [])
            parents = graph.get("parents", [])
            parent_units = graph.get("parent_units", [])

            task_text = ""
            child_text = ""
            parent_text = ""
            relationship_text = ""

            if intent == "relationship":
                organization = graph.get("organization")
                unit = graph.get("unit")

                if organization and unit:
                        relationship_text = f"""
                Organisasi: {organization}
                UPTD: {unit}
                Relasi: MEMILIKI_UPTD
                """

            for task in tasks:
                if not task.get("name"):
                    continue

                task_text += f"""
- {task.get("name")}
  Sumber: {task.get("regulation")}
  Pasal: {task.get("pasal")}
  Ayat: {task.get("ayat")}
  Halaman: {task.get("page")}
"""

            graph_text += f"""
[Graph Entity {i}]
Entity: {entity}

Organisasi:
{graph.get("organization", [])}

Parent Unit:
{graph.get("parent_units", [])}

Parent Position:
{graph.get("parents", [])}

Unit di dalam:
{graph.get("children", [])}

Tugas:
{task_text}

Relationship:
{relationship_text}
"""

    user_info = ""

    if name:
        user_info = f"""
Nama pengguna: {name}
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
10. Jika nama pengguna tersedia dan sesuai dengan konteks
    percakapan, gunakan nama tersebut secara natural
    dalam sapaan atau jawaban.
11. Jangan menyebut nama pengguna secara berulang
    jika tidak diperlukan.
12. Jika pengguna memberikan sapaan seperti "hai" atau
    "halo" bersama pertanyaan, balas sapaan tersebut
    secara natural sebelum menjawab pertanyaannya.
13. Jika menggunakan greeting, letakkan greeting sebagai
    paragraf terpisah dari jawaban.

14. Jangan memasukkan greeting ke dalam numbered list
    atau bullet list.

15. Jika jawaban berupa daftar, letakkan kalimat pembuka
    terlebih dahulu, kemudian mulai daftar dari nomor 1.

16. Gunakan Markdown secara konsisten:
    - numbered list untuk daftar yang berurutan;
    - bullet list untuk daftar yang tidak berurutan;
    - paragraf terpisah untuk penjelasan;
    - bold hanya untuk bagian yang penting.

=== INFORMASI PENGGUNA ===
{user_info}

=== VECTOR CONTEXT ===
{vector_text}

=== GRAPH CONTEXT ===
{graph_text}

=== PERTANYAAN PENGGUNA ===
{question}

Berikan jawaban yang langsung menjawab pertanyaan.
"""

    return prompt.strip()


def build_multi_question_prompt(
    question_results: list[dict],
    name: str | None = None
) -> str:
    """
    Membuat prompt untuk beberapa sub-question.

    Setiap pertanyaan memiliki context masing-masing
    dan context tidak boleh dicampur antar pertanyaan.
    """

    question_sections = ""

    for index, item in enumerate(question_results, start=1):
        question = item["question"]
        context = item["context"]

        vector_context = context.get("vector_context", [])
        graph_context = context.get("graph_context")

        vector_text = ""

        if vector_context:
            for i, result in enumerate(
                vector_context,
                start=1
            ):
                vector_text += f"""
[Vector Result {i}]
Regulasi: {result.get("regulation_number")}
Pasal: {result.get("pasal")}
Ayat: {result.get("ayat")}
Halaman: {result.get("page")}
Isi: {result.get("content")}
"""

        graph_text = ""

        if graph_context:
            for i, item in enumerate(graph_context, start=1):
                entity = item.get("entity")
                intent = item.get("intent")
                graph = item.get("context", {})

                tasks = graph.get("tasks", [])
                children = graph.get("children", [])
                parents = graph.get("parents", [])
                parent_units = graph.get("parent_units", [])

                task_text = ""
                child_text = ""
                parent_text = ""
                relationship_text = ""

                # Tugas
                for task in tasks:
                    if not task.get("name"):
                        continue

                    task_text += f"""
        - {task.get("name")}
        Sumber: {task.get("regulation")}
        Pasal: {task.get("pasal")}
        Ayat: {task.get("ayat")}
        Halaman: {task.get("page")}
        """

                # Unit di dalam
                for child in children:
                    if not child.get("name"):
                        continue

                    child_text += f"""
        - {child.get("name")}
        Sumber: {child.get("regulation")}
        Pasal: {child.get("pasal")}
        Ayat: {child.get("ayat")}
        Halaman: {child.get("page")}
        """

                # Parent position
                for parent in parents:
                    if not parent.get("name"):
                        continue

                    parent_text += f"""
        - {parent.get("name")}
        Sumber: {parent.get("regulation")}
        Pasal: {parent.get("pasal")}
        Ayat: {parent.get("ayat")}
        Halaman: {parent.get("page")}
        """

                # Relationship
                if intent == "relationship":
                    organization = graph.get("organization")
                    unit = graph.get("unit")

                    if organization and unit:
                        relationship_text = f"""
        Organisasi: {organization}
        UPTD: {unit}
        Relasi: MEMILIKI_UPTD
        """

                graph_text += f"""
        [Graph Entity {i}]
        Entity: {entity}
        Intent: {intent}

        Parent Unit:
        {parent_units}

        Parent Position:
        {parent_text}

        Unit di dalam:
        {child_text}

        Tugas:
        {task_text}

        Relationship:
        {relationship_text}
        """

        question_sections += f"""
========================================
PERTANYAAN {index}
========================================

Pertanyaan:
{question}

VECTOR CONTEXT:
{vector_text if vector_text else "Tidak ada konteks vector yang relevan."}

GRAPH CONTEXT:
{graph_text if graph_text else "Tidak ada konteks graph yang relevan."}
"""

    user_info = ""

    if name:
        user_info = f"""
Nama pengguna: {name}
"""

    prompt = f"""
Kamu adalah chatbot informasi
Dinas Komunikasi, Informatika dan Persandian Aceh.

Jawab pertanyaan pengguna hanya berdasarkan konteks
yang diberikan di bawah ini.

Basis pengetahuan chatbot hanya berasal dari:

1. Peraturan Gubernur Aceh Nomor 119 Tahun 2016
2. Peraturan Gubernur Aceh Nomor 61 Tahun 2020

=== INFORMASI PENGGUNA ===
{user_info}

=== ATURAN JAWABAN ===

1. Jawab semua pertanyaan yang diberikan.

2. Jawab pertanyaan sesuai urutan pertanyaan.

3. Setiap pertanyaan memiliki context masing-masing.
   Gunakan hanya context yang berada pada bagian
   pertanyaan tersebut.

4. Jangan mencampurkan context dari satu pertanyaan
   dengan pertanyaan lainnya.

5. Jika sebuah pertanyaan memiliki context vector
   dan graph, gunakan informasi tersebut secara
   bersama jika memang relevan.

6. Jika sebuah pertanyaan tidak memiliki context
   yang relevan, katakan bahwa informasi tersebut
   tidak ditemukan dalam basis pengetahuan.

7. Jangan menggunakan pengetahuan di luar context
   yang diberikan.

8. Jangan mengarang informasi.

9. Jangan menambahkan informasi yang tidak diperlukan
   untuk menjawab pertanyaan.

10. Jika pertanyaan meminta beberapa informasi,
    pastikan seluruh bagian pertanyaan tersebut
    dijawab.

11. Gunakan bahasa Indonesia yang jelas, ringkas,
    dan mudah dipahami.

12. Jangan menyebutkan "Vector Context",
    "Graph Context", embedding, retrieval,
    database, atau proses internal sistem.

13. Jika nama pengguna tersedia dan sesuai dengan konteks
    percakapan, gunakan nama tersebut secara natural.
"""

    # Tambahan penutup string literal dan return statement yang sempat terpotong
    prompt += f"""
=== SECTIONS ===
{question_sections}
"""
    return prompt.strip()
