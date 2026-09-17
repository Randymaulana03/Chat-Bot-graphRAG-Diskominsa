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

    OPTIONAL MATCH (unit)-[:MEMILIKI_UNIT]->(child:Unit)

    OPTIONAL MATCH (unit)-[:BERADA_DI_BAWAH]->(parent:Position)

    OPTIONAL MATCH (unit)-[:MEMILIKI_TUGAS]->(task:Task)

    RETURN
        unit.name AS unit,
        collect(DISTINCT child.name) AS children,
        collect(DISTINCT parent.name) AS parents,
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

def find_entity(question: str):
    query = """
    MATCH (unit:Unit)
    WHERE toLower($question) CONTAINS toLower(unit.name)
    RETURN unit.name AS entity
    """

    with driver.session() as session:
        result = session.run(
            query,
            question=question
        )

        record = result.single()

        if record is None:
            return None

        return record["entity"]

def retrieve_graph_context(question: str):
    entity = find_entity(question)

    if entity is None:
        return None

    context = get_unit_context(entity)

    return {
        "entity": entity,
        "context": context
    }