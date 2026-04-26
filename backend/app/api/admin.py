"""Endpoints administrativos: reindexación y estadísticas."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Articulo, Chunk, Norma, QueryLog

logger = logging.getLogger(__name__)

router = APIRouter(tags=["admin"])


@router.get("/stats")
async def estadisticas(db: AsyncSession = Depends(get_db)):
    """Devuelve estadísticas del corpus y uso."""
    normas = await db.scalar(select(func.count(Norma.id)))
    articulos = await db.scalar(select(func.count(Articulo.id)))
    chunks = await db.scalar(select(func.count(Chunk.id)))
    consultas = await db.scalar(select(func.count(QueryLog.id)))
    latencia_promedio = await db.scalar(select(func.avg(QueryLog.latencia_ms)))

    return {
        "corpus": {
            "normas": normas or 0,
            "articulos": articulos or 0,
            "chunks": chunks or 0,
        },
        "uso": {
            "consultas_totales": consultas or 0,
            "latencia_promedio_ms": round(latencia_promedio or 0, 1),
        },
    }


@router.post("/reindex")
async def reindexar(db: AsyncSession = Depends(get_db)):
    """Dispara una reindexación del corpus (ejecuta bootstrap_corpus)."""
    from app.ingestion.pipeline import ejecutar_ingesta

    try:
        resultado = await ejecutar_ingesta(db)
        return {"status": "ok", "resultado": resultado}
    except Exception as e:
        logger.exception("Error en reindexación")
        return {"status": "error", "detalle": str(e)}
