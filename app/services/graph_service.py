from app.core.neo4j_client import driver


def get_unit_task(task_name: str):
    query = """
    MATCH (unit:Unit)-[:MEMILIKI_TUGAS]->(task:Task)
    WHERE task.name = $task_name
    RETURN unit.name AS unit, task.name AS task
    """

    with driver.session() as session:
        result = session.run(
            query,
            task_name=task_name
        )

        return [record.data() for record in result]

def get_unit_parent(unit_name: str):
    query = """
    MATCH (unit:Unit {
        name: $unit_name
    })-[:BERADA_DI_BAWAH]->(position:Position)
    RETURN unit.name AS unit,
           position.name AS parent
    """

    with driver.session() as session:
        result = session.run(
            query,
            unit_name=unit_name
        )

        return [record.data() for record in result]

def get_unit_children(unit_name: str):
    query = """
    MATCH (parent:Unit {
        name: $unit_name
    })-[:MEMILIKI_UNIT]->(unit:Unit)
    RETURN parent.name AS parent,
           unit.name AS unit
    """

    with driver.session() as session:
        result = session.run(
            query,
            unit_name=unit_name
        )

        return [record.data() for record in result]

def get_unit_context(unit_name: str):
    query = """
    MATCH (unit:Unit {
        name: $unit_name
    })

    OPTIONAL MATCH (organization:Organization)-[:MEMILIKI_UPTD]->(unit)

    OPTIONAL MATCH (parent_unit:Unit)-[:MEMILIKI_UNIT]->(unit)

    OPTIONAL MATCH (unit)-[:MEMILIKI_UNIT]->(child:Unit)

    OPTIONAL MATCH (unit)-[:BERADA_DI_BAWAH]->(parent:Position)

    OPTIONAL MATCH (unit)-[:MEMILIKI_TUGAS]->(task:Task)

    RETURN
        unit.name AS unit,
        collect(DISTINCT organization.name) AS organizations,
        collect(DISTINCT parent_unit.name) AS parent_units,
        collect(DISTINCT parent.name) AS parents,
        collect(DISTINCT child.name) AS children,
        collect(DISTINCT task.name) AS tasks
    """

    with driver.session() as session:
        result = session.run(
            query,
            unit_name=unit_name
        )

        record = result.single()

        if record is None:
            return None

        return record.data()

def find_entities(question: str):
    query = """
    MATCH (entity)
    WHERE entity.name IS NOT NULL
      AND toLower($question) CONTAINS toLower(entity.name)

    RETURN
        labels(entity) AS labels,
        entity.name AS entity
    """

    with driver.session() as session:
        result = session.run(
            query,
            question=question
        )

        return [
            {
                "entity": record["entity"],
                "labels": record["labels"],
            }
            for record in result
        ]

def retrieve_graph_context(question: str):
    entities = find_entities(question)

    if not entities:
        return None

    contexts = []

    for item in entities:
        entity = item["entity"]
        labels = item["labels"]

        if "Unit" not in labels:
            continue

        context = get_unit_context(entity)

        if context is not None:
            contexts.append({
                "entity": entity,
                "context": context,
            })

    if not contexts:
        return None

    return contexts

def is_graph_context_relevant(question: str, graph_context: list[dict]) -> bool:
    if not graph_context:
        return False

    question_lower = question.lower()

    # Pertanyaan yang membutuhkan struktur organisasi
    structure_keywords = [
        "unit",
        "seksi",
        "bagian",
        "subbagian",
        "struktur",
        "di dalam",
        "terdapat",
    ]

    # Pertanyaan tentang tugas/fungsi
    task_keywords = [
        "tugas",
        "fungsi",
    ]

    # Pertanyaan tentang kepemimpinan / hubungan organisasi
    relation_keywords = [
        "di bawah siapa",
        "bertanggung jawab kepada siapa",
        "dipimpin siapa",
        "siapa yang memimpin",
        "memimpin",
        "hubungan",
    ]

    # Pertanyaan tentang organisasi tempat unit berada
    organization_keywords = [
        "organisasi",
        "dinas",
        "berada pada",
        "bagian dari",
    ]

    # Pertanyaan yang meminta data spesifik yang tidak
    # direpresentasikan oleh graph kita
    unsupported_keywords = [
        "nama",
        "berapa",
        "jumlah",
        "alamat",
        "lokasi",
        "anggaran",
        "pegawai",
        "orang",
    ]

    if any(keyword in question_lower for keyword in unsupported_keywords):
        return False

    if any(keyword in question_lower for keyword in structure_keywords):
        return True

    if any(keyword in question_lower for keyword in task_keywords):
        return True

    if any(keyword in question_lower for keyword in relation_keywords):
        return True

    if any(keyword in question_lower for keyword in organization_keywords):
        return True

    return False