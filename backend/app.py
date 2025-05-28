import logging
from fastapi import FastAPI
from services.neo4j import get_driver, close_driver

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """
    Se ejecuta al iniciar la aplicación.
    Probaremos la conexión a Neo4j lanzando una consulta trivial.
    """
    try:
        driver = get_driver()
        # Abrimos una sesión y lanzamos un RETURN 1 AS test
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            record = result.single()
            if record and record["test"] == 1:
                logging.info("✅ Conexión a Neo4j establecida correctamente.")
            else:
                logging.error("❌ Conexión a Neo4j, pero la query de prueba no devolvió el resultado esperado.")
    except Exception as e:
        logging.error(f"❌ Error al conectar con Neo4j: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Se ejecuta al apagar la aplicación.
    Cerramos el driver para liberar recursos.
    """
    try:
        close_driver()
        logging.info("🔌 Driver de Neo4j cerrado correctamente.")
    except Exception as e:
        logging.error(f"⚠️ Error al cerrar el driver de Neo4j: {e}")

# Ejemplo de endpoint para comprobar que la API levanta
@app.get("/ping")
async def ping():
    return {"message": "pong"}