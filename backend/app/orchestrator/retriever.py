"""Retriever híbrido: búsqueda vectorial (pgvector) + BM25 sobre metadatos."""

import logging
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Articulo, Chunk, Norma
from app.utils.embeddings import generar_embedding_query

logger = logging.getLogger(__name__)


async def recuperar_chunks(
    pregunta: str,
    db: AsyncSession,
    top_k: int | None = None,
    filtros: dict | None = None,
) -> list[dict]:
    """Recupera los chunks más relevantes usando búsqueda híbrida.

    1. Búsqueda vectorial por similitud coseno
    2. Búsqueda BM25 por keywords en título/número de norma
    3. Fusión de resultados con ponderación
    """
    top_k = top_k or settings.retrieval_top_k
    filtros = filtros or {}

    # Búsquedas en paralelo
    resultados_vectorial = await _busqueda_vectorial(pregunta, db, top_k * 2, filtros)
    resultados_keyword = await _busqueda_keyword(pregunta, db, top_k, filtros)

    # Fusionar y deduplicar (Reciprocal Rank Fusion simplificado)
    fusionados = _fusionar_resultados(resultados_vectorial, resultados_keyword, top_k)

    logger.info(
        "Recuperados %d chunks (vectorial=%d, keyword=%d)",
        len(fusionados),
        len(resultados_vectorial),
        len(resultados_keyword),
    )

    return fusionados


async def _busqueda_vectorial(
    pregunta: str,
    db: AsyncSession,
    top_k: int,
    filtros: dict,
) -> list[dict]:
    """Búsqueda por similitud vectorial en pgvector."""
    try:
        query_embedding = await generar_embedding_query(pregunta)
    except Exception:
        logger.warning("Error generando embedding de query, cayendo a solo keyword")
        return []

    # Construir query con filtros opcionales
    stmt = (
        select(
            Chunk,
            Articulo,
            Norma,
            Chunk.embedding.cosine_distance(query_embedding).label("distancia"),
        )
        .join(Articulo, Chunk.articulo_id == Articulo.id)
        .join(Norma, Articulo.norma_id == Norma.id)
        .where(Chunk.embedding.isnot(None))
        .where(Articulo.vigente.is_(True))
        .where(Norma.derogada.is_(False))
    )

    if "organismo" in filtros:
        stmt = stmt.where(Norma.organismo == filtros["organismo"])

    stmt = stmt.order_by("distancia").limit(top_k)

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "chunk_id": str(row.Chunk.id),
            "articulo_id": str(row.Articulo.id),
            "texto": row.Chunk.texto,
            "norma_tipo": row.Norma.tipo,
            "norma_numero": row.Norma.numero,
            "norma_titulo": row.Norma.titulo,
            "articulo_numero": row.Articulo.numero,
            "articulo_path": row.Articulo.path,
            "url_oficial": row.Norma.url_oficial,
            "organismo": row.Norma.organismo,
            "score": 1.0 - row.distancia,  # Convertir distancia a similitud
            "fuente": "vectorial",
        }
        for row in rows
    ]


async def _busqueda_keyword(
    pregunta: str,
    db: AsyncSession,
    top_k: int,
    filtros: dict,
) -> list[dict]:
    """Búsqueda por keywords en título de norma y número de artículo."""
    palabras = [p.strip().lower() for p in pregunta.split() if len(p.strip()) > 2]
    if not palabras:
        return []

    # Buscar coincidencias en título de norma o path de artículo
    condiciones = []
    for palabra in palabras[:10]:  # Limitar a 10 palabras
        condiciones.append(func.lower(Norma.titulo).contains(palabra))
        condiciones.append(func.lower(Articulo.path).contains(palabra))
        condiciones.append(func.lower(Chunk.texto).contains(palabra))

    stmt = (
        select(Chunk, Articulo, Norma)
        .join(Articulo, Chunk.articulo_id == Articulo.id)
        .join(Norma, Articulo.norma_id == Norma.id)
        .where(or_(*condiciones))
        .where(Articulo.vigente.is_(True))
        .where(Norma.derogada.is_(False))
    )

    if "organismo" in filtros:
        stmt = stmt.where(Norma.organismo == filtros["organismo"])

    stmt = stmt.limit(top_k)

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "chunk_id": str(row.Chunk.id),
            "articulo_id": str(row.Articulo.id),
            "texto": row.Chunk.texto,
            "norma_tipo": row.Norma.tipo,
            "norma_numero": row.Norma.numero,
            "norma_titulo": row.Norma.titulo,
            "articulo_numero": row.Articulo.numero,
            "articulo_path": row.Articulo.path,
            "url_oficial": row.Norma.url_oficial,
            "organismo": row.Norma.organismo,
            "score": 0.5,  # Score fijo para keyword
            "fuente": "keyword",
        }
        for row in rows
    ]


def _fusionar_resultados(
    vectorial: list[dict],
    keyword: list[dict],
    top_k: int,
) -> list[dict]:
    """Fusiona resultados de ambas búsquedas con Reciprocal Rank Fusion."""
    scores: dict[str, float] = {}
    chunks_por_id: dict[str, dict] = {}

    k = 60  # Constante RRF

    # Scores vectoriales
    for i, chunk in enumerate(vectorial):
        cid = chunk["chunk_id"]
        scores[cid] = scores.get(cid, 0) + 1.0 / (k + i + 1)
        chunks_por_id[cid] = chunk

    # Scores keyword (peso menor)
    for i, chunk in enumerate(keyword):
        cid = chunk["chunk_id"]
        scores[cid] = scores.get(cid, 0) + 0.5 / (k + i + 1)
        if cid not in chunks_por_id:
            chunks_por_id[cid] = chunk

    # Ordenar por score fusionado
    ordenados = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    resultado = []
    for cid, score in ordenados[:top_k]:
        chunk = chunks_por_id[cid]
        chunk["score_fusionado"] = score
        resultado.append(chunk)

    return resultado
