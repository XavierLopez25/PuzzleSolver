import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Carga variables de entorno desde un archivo .env si existe
load_dotenv()

# Lee credenciales de Neo4j
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

if not all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD]):
    raise ValueError(
        "Por favor define las variables de entorno NEO4J_URI, NEO4J_USERNAME y NEO4J_PASSWORD"
    )

# Singleton para el driver de Neo4j
_driver = None

def get_driver() -> GraphDatabase.driver:
    """
    Inicializa y retorna un driver de Neo4j singleton.
    """
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    return _driver


def get_session():
    """
    Retorna una nueva sesión de Neo4j.
    Uso:
        with get_session() as session:
            session.run(...)
    """
    driver = get_driver()
    return driver.session(database=NEO4J_DATABASE)

def close_driver():
    """Cierra el driver (llamar al apagar la app)."""
    _driver.close()
