from app.core.neo4j_client import driver


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

    intents = detect_graph_intents(question)

    if not intents:
        return None

    contexts = []

    for item in entities:
        entity = item["entity"]
        labels = item["labels"]

        for intent in intents:
            context = None

            if intent == "task" and "Unit" in labels:
                context = get_unit_task_context(entity)

            elif intent == "leadership" and "Unit" in labels:
                context = get_unit_leadership_context(entity)

            elif intent == "leadership" and "Organization" in labels:
                context = get_organization_leadership_context(entity)

            elif intent == "parent" and "Unit" in labels:
                context = get_unit_parent_unit_context(entity)

            elif intent == "structure" and "Unit" in labels:
                context = get_unit_structure_context(entity)

            elif intent == "organization" and "Unit" in labels:
                context = get_unit_context(entity)

            elif intent == "organization" and "Organization" in labels:
                context = get_organization_context(entity)

            elif intent == "relationship" and "Unit" in labels:
                context = get_unit_organization_context(entity)

            if context is not None:
                contexts.append({
                    "entity": entity,
                    "intent": intent,
                    "context": context,
                })

    if not contexts:
        return None

    return contexts

def detect_graph_intents(question: str) -> list[str]:
    question_lower = question.lower()

    task_keywords = [
        "tugas",
        "fungsi",
        "tugas dan fungsi",
        "tugas pokok",
        "fungsi pokok",
        "tugas utama",
        "fungsi utama",
        "pelaksanaan tugas",
        "pelaksanaan fungsi",
        "melaksanakan tugas",
        "melaksanakan fungsi",
        "melaksanakan kegiatan",
        "kegiatan yang dilaksanakan",
        "kegiatan yang dilakukan",
        "kegiatan teknis",
        "kegiatan operasional",
        "bertugas",
        "tugasnya",
        "fungsinya",
        "apa tugasnya",
        "apa fungsinya",
        "tugasnya apa",
        "fungsinya apa",
        "apa yang dikerjakan",
        "apa yang dilakukan",
        "apa yang dilaksanakan",
        "apa saja tugas",
        "apa saja fungsi",
        "kerjaannya",
        "kerjaan",
        "kerjanya",
        "kerja apa",
        "kerjanya apa",
        "kerjaan apa",
        "kerjaan apa saja",
        "kerjanya ngapain",
        "kerja ngapain",
        "ngapain",
        "ngapain aja",
        "ngapain saja",
        "melakukan apa",
        "melakukan apa saja",
        "ngurus apa",
        "ngurus apa saja",
        "mengurus apa",
        "mengurus apa saja",
        "yang diurus apa",
        "yang dikerjakan apa",
        "apa yang dikerjain",
        "biasanya ngapain",
        "biasanya mengerjakan apa",
        "sebenarnya kerja apa",
        "sebenarnya kerjanya apa",
        "sebenarnya tugasnya apa",
        "sebenarnya fungsinya apa",
        "itu ngurus apa",
        "itu kerja apa",
        "itu tugasnya apa",
        "itu fungsinya apa",
        "dia ngurus apa",
        "dia kerja apa",
        "dia tugasnya apa",
        "mereka ngurus apa",
        "mereka kerja apa",
        "mereka tugasnya apa",
        "tanggung jawab",
        "apa tanggung jawabnya",
        "apa saja tanggung jawab",
        "ruang lingkup tugas",
        "ruang lingkup fungsi",
        "peran",
        "perannya",
        "apa perannya",
        "perannya apa",
        "peran dan tugas",
        "peran serta tugas",
    ]

    leadership_keywords = [
        "siapa yang memimpin",
        "dipimpin oleh siapa",
        "dipimpin siapa",
        "pimpinan",
        "pemimpin",
        "kepala uptd",
        "jabatan pimpinan",
        "yang memimpin",
        "pihak yang memimpin",
        "bertanggung jawab kepada",
        "siapa yang ngepalai",
        "siapa yang memimpin unit ini",
        "siapa kepala",
        "siapa orang yang memimpin",
        "siapa atasannya",
        "atasannya siapa",
        "bosnya siapa",
        "dipimpin sama siapa",
        "yang jadi kepala siapa",
        "yang jadi pimpinan siapa",
        "siapa yang bertanggung jawab",
    ]

    structure_keywords = [
        "struktur",
        "struktur organisasi",
        "susunan organisasi",
        "susunan",
        "unit",
        "unit kerja",
        "bidang",
        "bidang-bidang",
        "seksi",
        "seksi-seksi",
        "bagian",
        "bagian-bagian",
        "subbagian",
        "subbagian-subbagian",
        "organisasi",
        "unsur organisasi",
        "perangkat organisasi",
        "unit organisasi",
        "unit di dalam",
        "unit yang terdapat",
        "unit yang ada",
        "unit yang berada",
        "bidang yang terdapat",
        "bidang yang ada",
        "seksi yang terdapat",
        "seksi yang ada",
        "bagian yang terdapat",
        "bagian yang ada",
        "terdiri dari",
        "terdiri atas",
        "membawahi",
        "membawahkan",
        "di bawahnya terdapat",
        "isinya apa saja",
        "di dalamnya ada apa",
        "di dalamnya ada apa saja",
        "ada unit apa saja",
        "ada bidang apa saja",
        "ada seksi apa saja",
        "ada bagian apa saja",
        "terdapat apa saja",
        "punya bidang apa saja",
        "punya seksi apa saja",
        "punya unit apa saja",
        "unitnya apa saja",
        "bidangnya apa saja",
        "seksinya apa saja",
        "bagiannya apa saja",
    ]

    organization_keywords = [
        "kedudukan",
        "kedudukan organisasi",
        "kedudukan dinas",
        "berkedudukan",
        "kedudukan dan susunan",
        "susunan dan tata kerja",
        "posisinya di mana",
        "posisinya dalam organisasi",
        "bagian dari apa",
        "termasuk bagian apa",
        "masuk ke bagian mana",
        "ada di bawah siapa",
        "berada di bawah siapa",
        "termasuk organisasi mana",
        "ini bagian dari mana",
    ]

    parent_keywords = [
        "berada di bawah siapa",
        "berada dibawah siapa",
        "di bawah siapa",
        "dibawah siapa",
        "berada di bidang apa",
        "berada di bawah bidang apa",
        "termasuk bidang apa",
        "bagian dari bidang apa",
        "berada dalam bidang apa",
        "masuk ke bidang mana",
        "berada di unit apa",
        "berada dalam unit apa",
        "termasuk unit apa",
        "bagian dari unit apa",
    ]

    relationship_keywords = [
        "hubungan",
        "hubungannya",
        "berhubungan dengan",
        "kaitannya dengan",
        "kaitan dengan",
        "relasinya dengan",
    ]

    intents = []

    # TASK
    if any(keyword in question_lower for keyword in task_keywords):
        intents.append("task")

    # LEADERSHIP
    if any(keyword in question_lower for keyword in leadership_keywords):
        intents.append("leadership")

    # RELATIONSHIP
    if any(keyword in question_lower for keyword in relationship_keywords):
        intents.append("relationship")

    # PARENT
    elif any(keyword in question_lower for keyword in parent_keywords):
        intents.append("parent")

    # STRUCTURE
    elif any(keyword in question_lower for keyword in structure_keywords):
        intents.append("structure")

    # ORGANIZATION
    elif any(keyword in question_lower for keyword in organization_keywords):
        intents.append("organization")

    return intents

def get_unit_task_context(unit_name: str):
    query = """
    MATCH (unit:Unit {
        name: $unit_name
    })

    OPTIONAL MATCH (unit)-[:MEMILIKI_TUGAS]->(direct_task:Task)
    OPTIONAL MATCH (unit)-[:MEMILIKI_UNIT]->(child:Unit)
                         -[:MEMILIKI_TUGAS]->(child_task:Task)

    WITH
        unit,
        collect(DISTINCT direct_task) AS direct_tasks,
        collect(DISTINCT {
            unit: child,
            task: child_task
        }) AS child_tasks

    RETURN
        unit.name AS unit,

        [
            task IN direct_tasks
            WHERE task IS NOT NULL |
            {
                unit: unit.name,
                name: task.name,
                regulation: task.regulation,
                pasal: task.pasal,
                ayat: task.ayat,
                page: task.page
            }
        ]
        +
        [
            item IN child_tasks
            WHERE item.unit IS NOT NULL
              AND item.task IS NOT NULL |
            {
                unit: item.unit.name,
                name: item.task.name,
                regulation: item.task.regulation,
                pasal: item.task.pasal,
                ayat: item.task.ayat,
                page: item.task.page
            }
        ] AS tasks
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
        }) AS leaders
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

def get_organization_leadership_context(organization_name: str):
    query = """
    MATCH (position:Position)-[rel:MEMIMPIN]->(organization:Organization {
        name: $organization_name
    })

    RETURN
        organization.name AS organization,
        collect(DISTINCT {
            name: position.name,
            regulation: rel.regulation,
            pasal: rel.pasal,
            ayat: rel.ayat,
            page: rel.page
        }) AS leaders
    """

    with driver.session() as session:
        result = session.run(
            query,
            organization_name=organization_name
        )

        record = result.single()

        if record is None:
            return None

        return record.data()

def get_unit_parent_unit_context(unit_name: str):
    query = """
    MATCH (unit:Unit {
        name: $unit_name
    })

    OPTIONAL MATCH (parent:Unit)-[:MEMILIKI_UNIT]->(unit)

    OPTIONAL MATCH (unit)-[under_rel:BERADA_DI_BAWAH]->(position:Position)

    OPTIONAL MATCH (unit)-[:BERASAL_DARI]->(source:Source)

    RETURN
        unit.name AS unit,

        collect(DISTINCT {
            name: parent.name,
            regulation: source.regulation,
            pasal: source.pasal,
            ayat: source.ayat,
            page: source.page
        }) AS parents,

        collect(DISTINCT {
            name: position.name,
            regulation: under_rel.regulation,
            pasal: under_rel.pasal,
            ayat: under_rel.ayat,
            page: under_rel.page
        }) AS leaders
    """

    with driver.session() as session:
        result = session.run(
            query,
            unit_name=unit_name
        )

        record = result.single()

        if record is None:
            return None

        data = record.data()

        data["parents"] = [
            parent
            for parent in data.get("parents", [])
            if parent.get("name")
        ]

        data["leaders"] = [
            leader
            for leader in data.get("leaders", [])
            if leader.get("name")
        ]

        return data


def get_organization_context(organization_name: str):
    query = """
    MATCH (organization:Organization {
        name: $organization_name
    })

    OPTIONAL MATCH (position:Position)-[lead_rel:MEMIMPIN]->(organization)
    OPTIONAL MATCH (organization)-[:MEMILIKI_UPTD]->(unit:Unit)

    RETURN
        organization.name AS organization,
        collect(DISTINCT {
            name: position.name,
            regulation: lead_rel.regulation,
            pasal: lead_rel.pasal,
            ayat: lead_rel.ayat,
            page: lead_rel.page
        }) AS leaders,
        collect(DISTINCT unit.name) AS units
    """

    with driver.session() as session:
        result = session.run(
            query,
            organization_name=organization_name
        )

        record = result.single()

        if record is None:
            return None

        return record.data()


def get_unit_organization_context(unit_name: str):
    query = """
    MATCH (organization:Organization)-[:MEMILIKI_UPTD]->(unit:Unit {
        name: $unit_name
    })

    OPTIONAL MATCH (unit)-[:BERASAL_DARI]->(source:Source)

    RETURN
        organization.name AS organization,
        unit.name AS unit,
        collect({
            regulation: source.regulation,
            year: source.year,
            type: source.type
        }) AS sources
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
