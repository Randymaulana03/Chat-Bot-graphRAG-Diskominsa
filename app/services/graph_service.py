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
        OPTIONAL MATCH (child)-[:BERASAL_DARI]->(child_source:Source)
        OPTIONAL MATCH (unit)-[parent_rel:BERADA_DI_BAWAH]->(parent:Position)
        OPTIONAL MATCH (unit)-[:MEMILIKI_TUGAS]->(task:Task)
        OPTIONAL MATCH (task)-[:BERASAL_DARI]->(source:Source)

        RETURN
            unit.name AS unit,
            collect(DISTINCT organization.name) AS organizations,
            collect(DISTINCT parent_unit.name) AS parent_units,

            collect(DISTINCT {
                name: parent.name,
                regulation: parent_rel.regulation,
                pasal: parent_rel.pasal,
                ayat: parent_rel.ayat,
                page: parent_rel.page
            }) AS parents,

            collect(DISTINCT {
                name: child.name,
                regulation: child_source.regulation,
                pasal: child_source.pasal,
                ayat: child_source.ayat,
                page: child_source.page
            }) AS children,

            collect(DISTINCT {
                name: task.name,
                regulation: source.regulation,
                pasal: source.pasal,
                ayat: source.ayat,
                page: source.page
        }) AS tasks
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

    intent = detect_graph_intent(question)

    if intent is None:
        return None

    contexts = []

    for item in entities:
        entity = item["entity"]
        labels = item["labels"]

        if "Unit" not in labels:
            continue

        context = None

        if intent == "task":
            context = get_unit_task_context(entity)

        elif intent == "leadership":
            context = get_unit_leadership_context(entity)

        elif intent == "structure":
            context = get_unit_structure_context(entity)

        elif intent == "organization":
            context = get_unit_context(entity)

        if context is not None:
            contexts.append({
                "entity": entity,
                "intent": intent,
                "context": context,
            })

    if not contexts:
        return None

    return contexts

def is_graph_context_relevant(
    question: str,
    graph_context: list[dict]
) -> bool:

    if not graph_context:
        return False

    return detect_graph_intent(question) is not None
    
def detect_graph_intent(question: str) -> str | None:
    question_lower = question.lower()

    task_keywords = [
        "tugas",
        "fungsi",
    ]

    leadership_keywords = [
        "siapa yang memimpin",
        "dipimpin siapa",
        "di bawah siapa",
        "bertanggung jawab kepada siapa",
        "memimpin",
    ]

    structure_keywords = [
        "unit",
        "seksi",
        "bagian",
        "subbagian",
        "struktur",
        "di dalam",
        "terdapat",
    ]

    organization_keywords = [
        "organisasi",
        "dinas",
        "berada pada",
        "bagian dari",
    ]

    if any(
        keyword in question_lower
        for keyword in task_keywords
    ):
        return "task"

    if any(
        keyword in question_lower
        for keyword in leadership_keywords
    ):
        return "leadership"

    if any(
        keyword in question_lower
        for keyword in structure_keywords
    ):
        return "structure"

    if any(
        keyword in question_lower
        for keyword in organization_keywords
    ):
        return "organization"

    return None

def get_unit_task_context(unit_name: str):
    query = """
    MATCH (unit:Unit {
        name: $unit_name
    })-[rel:MEMILIKI_TUGAS]->(task:Task)
    OPTIONAL MATCH (task)-[:BERASAL_DARI]->(source:Source)

    RETURN
        unit.name AS unit,
        collect(DISTINCT {
            name: task.name,
            regulation: source.regulation,
            pasal: source.pasal,
            ayat: source.ayat,
            page: source.page
        }) AS tasks
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

def get_unit_leadership_context(unit_name: str):
    query = """
    MATCH (unit:Unit {
        name: $unit_name
    })-[rel:BERADA_DI_BAWAH]->(position:Position)

    RETURN
        unit.name AS unit,
        collect(DISTINCT {
            name: position.name,
            regulation: rel.regulation,
            pasal: rel.pasal,
            ayat: rel.ayat,
            page: rel.page
        }) AS parents
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

def get_unit_structure_context(unit_name: str):
    query = """
    MATCH (unit:Unit {
        name: $unit_name
    })-[:MEMILIKI_UNIT]->(child:Unit)

    OPTIONAL MATCH (child)-[:BERASAL_DARI]->(source:Source)

    RETURN
        unit.name AS unit,
        collect(DISTINCT {
            name: child.name,
            regulation: source.regulation,
            pasal: source.pasal,
            ayat: source.ayat,
            page: source.page
        }) AS children
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
