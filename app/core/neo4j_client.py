from neo4j import GraphDatabase

from app.core.config import settings


driver = GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(
        settings.NEO4J_USERNAME,
        settings.NEO4J_PASSWORD
    ),
    max_connection_lifetime=300,     
    liveness_check_timeout=30,       
    max_connection_pool_size=50
)


def verify_connection():
    driver.verify_connectivity()
    return True