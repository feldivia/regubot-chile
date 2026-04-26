"""Pipeline de ingesta: orquesta scraping, parsing, chunking y almacenamiento."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.base import NormaRaw
from app.ingestion.chunker import chunkear_articulo
from app.ingestion.leychile import LeyChileScraper
from app.ingestion.parser import parsear_norma
from app.models import Articulo, Chunk, Norma
from app.utils.embeddings import generar_embeddings

logger = logging.getLogger(__name__)


async def ejecutar_ingesta(
    db: AsyncSession,
    identificadores: list[str] | None = None,
) -> dict:
    """Ejecuta el pipeline completo de ingesta.

    1. Scraping de fuentes
    2. Parsing estructural
    3. Chunking
    4. Generación de embeddings
    5. Almacenamiento en DB

    Idempotente: detecta cambios por hash y solo actualiza lo necesario.
    """
    resultado = {"normas_nuevas": 0, "normas_actualizadas": 0, "chunks_creados": 0, "errores": 0}

    # 1. Scraping
    scraper = LeyChileScraper()
    normas_raw = await scraper.obtener_normas(identificadores)
    logger.info("Scraping completado: %d normas obtenidas", len(normas_raw))

    for raw in normas_raw:
        try:
            await _procesar_norma(db, raw, resultado)
        except Exception:
            logger.exception("Error procesando norma %s %s", raw.tipo, raw.numero)
            resultado["errores"] += 1

    await db.commit()
    logger.info("Ingesta completada: %s", resultado)
    return resultado


async def _procesar_norma(db: AsyncSession, raw: NormaRaw, resultado: dict) -> None:
    """Procesa una norma individual: parsea, chunkea y almacena."""
    # Verificar si ya existe y si cambió
    existente = await db.scalar(
        select(Norma).where(Norma.tipo == raw.tipo, Norma.numero == raw.numero)
    )

    if existente and existente.hash_contenido == raw.hash_contenido:
        logger.debug("Sin cambios: %s %s", raw.tipo, raw.numero)
        return

    # 2. Parsing
    parsed = parsear_norma(raw)

    if existente:
        # Actualizar norma existente: eliminar artículos/chunks antiguos
        await db.execute(
            select(Articulo).where(Articulo.norma_id == existente.id)
        )
        # Eliminar artículos viejos (cascade elimina chunks)
        for art in await db.scalars(
            select(Articulo).where(Articulo.norma_id == existente.id)
        ):
            await db.delete(art)

        existente.hash_contenido = parsed.hash_contenido
        existente.titulo = parsed.titulo
        existente.derogada = parsed.derogada
        norma_db = existente
        resultado["normas_actualizadas"] += 1
    else:
        # Crear norma nueva
        norma_db = Norma(
            tipo=parsed.tipo,
            numero=parsed.numero,
            titulo=parsed.titulo,
            organismo=parsed.organismo,
            url_oficial=parsed.url_oficial,
            fecha_publicacion=None,  # TODO: parsear fecha
            hash_contenido=parsed.hash_contenido,
            derogada=parsed.derogada,
        )
        db.add(norma_db)
        await db.flush()  # Para obtener el ID
        resultado["normas_nuevas"] += 1

    # 3. Crear artículos y chunks
    todos_los_chunks_texto = []
    chunks_info = []  # (articulo_index, chunk_data)

    for art_parsed in parsed.articulos:
        articulo_db = Articulo(
            norma_id=norma_db.id,
            path=art_parsed.path,
            numero=art_parsed.numero,
            texto=art_parsed.texto,
            orden=art_parsed.orden,
            vigente=True,
        )
        db.add(articulo_db)
        await db.flush()

        chunks = chunkear_articulo(art_parsed, parsed.titulo)
        for chunk_data in chunks:
            todos_los_chunks_texto.append(chunk_data["texto"])
            chunks_info.append((articulo_db.id, chunk_data))

    # 4. Generar embeddings en batch
    if todos_los_chunks_texto:
        try:
            embeddings = await generar_embeddings(todos_los_chunks_texto)
        except Exception:
            logger.exception("Error generando embeddings para %s %s", raw.tipo, raw.numero)
            embeddings = [None] * len(todos_los_chunks_texto)

        # 5. Almacenar chunks con embeddings
        for i, (articulo_id, chunk_data) in enumerate(chunks_info):
            chunk_db = Chunk(
                articulo_id=articulo_id,
                texto=chunk_data["texto"],
                embedding=embeddings[i] if embeddings[i] else None,
                metadata_=chunk_data.get("metadata"),
                tokens=chunk_data.get("tokens"),
            )
            db.add(chunk_db)
            resultado["chunks_creados"] += 1
