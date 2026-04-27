"""Script idempotente para ingesta inicial del corpus normativo."""

import asyncio
import logging
import sys
from pathlib import Path

# Agregar el directorio raíz del backend al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402
from app.db.session import async_session, engine  # noqa: E402
from app.ingestion.pipeline import ejecutar_ingesta  # noqa: E402
from app.models.base import Base  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """Ejecuta la ingesta completa del corpus."""
    logger.info("=== Iniciando bootstrap del corpus ReguBot Chile ===")
    logger.info("Base de datos: %s", settings.database_url.split("@")[-1])

    # Crear tablas si no existen
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Ejecutar ingesta
    async with async_session() as db:
        resultado = await ejecutar_ingesta(db)

    logger.info("=== Bootstrap completado ===")
    logger.info("Normas nuevas: %d", resultado["normas_nuevas"])
    logger.info("Normas actualizadas: %d", resultado["normas_actualizadas"])
    logger.info("Chunks creados: %d", resultado["chunks_creados"])
    logger.info("Errores: %d", resultado["errores"])

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
