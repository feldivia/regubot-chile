"""Job diario de reindexación del corpus normativo."""

import logging

from app.db.session import async_session
from app.ingestion.pipeline import ejecutar_ingesta

logger = logging.getLogger(__name__)


async def reindexar_corpus():
    """Ejecuta la reindexación diaria detectando cambios por hash."""
    logger.info("Iniciando reindexación diaria")
    try:
        async with async_session() as db:
            resultado = await ejecutar_ingesta(db)
            logger.info("Reindexación completada: %s", resultado)
    except Exception:
        logger.exception("Error en reindexación diaria")
