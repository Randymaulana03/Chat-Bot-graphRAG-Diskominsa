def build_multi_question_prompt(
    question_results: list[dict],
    name: str | None = None,
) -> str:
    """
    Build one prompt for one or more decomposed questions.

    Each question keeps its own retrieval context so evidence from one
    question cannot accidentally answer another question.
    """
    sections = []

    for index, item in enumerate(question_results, start=1):
        question = item["question"]
        context = item["context"]
        vector_context = context.get("vector_context") or []
        graph_context = context.get("graph_context") or []

        vector_lines = []
        for result_index, result in enumerate(vector_context, start=1):
            vector_lines.append(
                "\n".join([
                    f"[Vector Evidence {result_index}]",
                    f"Regulasi: {result.get('regulation_number')}",
                    f"Pasal: {result.get('pasal')}",
                    f"Ayat: {result.get('ayat')}",
                    f"Halaman: {result.get('page')}",
                    f"Isi: {result.get('content')}",
                ])
            )

        graph_lines = []
        for result_index, item in enumerate(graph_context, start=1):
            entity = item.get("entity")
            intent = item.get("intent")
            graph = item.get("context") or {}

            lines = [
                f"[Graph Evidence {result_index}]",
                f"Entity: {entity}",
                f"Intent: {intent}",
            ]

            organizations = graph.get("organizations") or []
            units = graph.get("units") or []
            parent_units = graph.get("parent_units") or []
            children = graph.get("children") or []
            leaders = graph.get("leaders") or []
            parents = graph.get("parents") or []
            tasks = graph.get("tasks") or []

            if organizations:
                lines.append(f"Organisasi: {organizations}")

            if units:
                lines.append(f"Unit: {units}")

            if parent_units:
                lines.append(f"Parent Unit: {parent_units}")

            valid_leaders = [
                leader for leader in leaders
                if leader.get("name")
            ]
            if valid_leaders:
                lines.append("Pimpinan:")
                for leader in valid_leaders:
                    lines.append(
                        f"- {leader.get('name')} | "
                        f"Regulasi: {leader.get('regulation')} | "
                        f"Pasal: {leader.get('pasal')} | "
                        f"Ayat: {leader.get('ayat')} | "
                        f"Halaman: {leader.get('page')}"
                    )

            if parents:
                lines.append("Parent:")
                for parent in parents:
                    lines.append(
                        f"- {parent.get('name')} | "
                        f"Regulasi: {parent.get('regulation')} | "
                        f"Pasal: {parent.get('pasal')} | "
                        f"Ayat: {parent.get('ayat')} | "
                        f"Halaman: {parent.get('page')}"
                    )

            if children:
                lines.append("Unit di dalam:")
                for child in children:
                    lines.append(
                        f"- {child.get('name')} | "
                        f"Regulasi: {child.get('regulation')} | "
                        f"Pasal: {child.get('pasal')} | "
                        f"Ayat: {child.get('ayat')} | "
                        f"Halaman: {child.get('page')}"
                    )

            if tasks:
                lines.append("Tugas:")
                for task in tasks:
                    lines.append(
                        f"- {task.get('name')} | "
                        f"Regulasi: {task.get('regulation')} | "
                        f"Pasal: {task.get('pasal')} | "
                        f"Ayat: {task.get('ayat')} | "
                        f"Halaman: {task.get('page')}"
                    )

            organization = graph.get("organization")
            unit = graph.get("unit")
            if organization and unit:
                lines.extend([
                    f"Relasi organisasi: {organization}",
                    f"UPTD: {unit}",
                    "Relasi: MEMILIKI_UPTD",
                ])

            graph_lines.append("\n".join(lines))

        sections.append(
            "\n".join([
                "========================================",
                f"PERTANYAAN {index}",
                "========================================",
                "",
                f"Pertanyaan: {question}",
                "",
                "VECTOR EVIDENCE:",
                "\n\n".join(vector_lines)
                if vector_lines
                else "Tidak ada evidence vector.",
                "",
                "GRAPH EVIDENCE:",
                "\n\n".join(graph_lines)
                if graph_lines
                else "Tidak ada evidence graph.",
            ])
        )

    user_info = f"Nama pengguna: {name}" if name else "Tidak ada."

    prompt = f"""
Kamu adalah chatbot informasi Dinas Komunikasi, Informatika dan Persandian Aceh.

Jawab hanya berdasarkan evidence yang diberikan.

Basis pengetahuan hanya berasal dari:
1. Peraturan Gubernur Aceh Nomor 119 Tahun 2016
2. Peraturan Gubernur Aceh Nomor 61 Tahun 2020

ATURAN:
1. Jawab setiap pertanyaan sesuai urutan.
2. Setiap pertanyaan hanya boleh menggunakan evidence pada bagiannya sendiri.
3. Jangan mencampurkan evidence antarpertanyaan.
4. Gunakan evidence graph dan vector bersama-sama jika keduanya mendukung jawaban.
5. Jika evidence tidak cukup untuk menjawab suatu pertanyaan, katakan bahwa informasi tersebut tidak ditemukan dalam basis pengetahuan.
6. Jangan menggunakan pengetahuan di luar evidence.
7. Jangan mengarang nama, jabatan, struktur, tugas, regulasi, pasal, ayat, atau fakta lain.
8. Jangan menyebut proses internal seperti embedding, retrieval, vector database, graph database, atau evidence kepada pengguna.
9. Jawab ringkas, jelas, dan natural dalam bahasa Indonesia.
10. Jika nama pengguna tersedia, gunakan secara natural dan tidak berulang.
11. Jika pertanyaan disertai sapaan, balas sapaan secara natural sebagai paragraf terpisah.
12. Untuk daftar, gunakan Markdown secara konsisten.
13. Jika evidence tidak cukup, katakan bahwa informasi tidak ditemukan dalam basis pengetahuan.
14. Jangan gunakan pengetahuan dari luar basis pengetahuan.
15. Jangan membuat informasi atau hubungan yang tidak ada di evidence.
16. Pertahankan istilah dan bentuk hubungan sebagaimana didukung oleh evidence.
17. Jangan memperkuat atau mengubah hubungan menjadi istilah yang lebih kuat.
18. Jika evidence menyatakan "berada di bawah", gunakan "berada di bawah".
19. Jika evidence menyatakan "bertanggung jawab kepada", gunakan "bertanggung jawab kepada".
20. Jangan mengganti hubungan tersebut dengan istilah seperti "memiliki", "mengelola", atau "mengawasi" kecuali istilah tersebut memang dinyatakan atau didukung secara eksplisit oleh evidence.

=== INFORMASI PENGGUNA ===
{user_info}

=== DATA PERTANYAAN ===
{chr(10).join(sections)}

Berikan jawaban akhir tanpa menjelaskan proses internal sistem.
"""

    return prompt.strip()
