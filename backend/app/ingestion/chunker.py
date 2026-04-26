"""Chunking estructural: respeta límites de artículos, nunca corta a la mitad."""

import logging

from app.ingestion.parser import ArticuloParsed

logger = logging.getLogger(__name__)

# Límites de tokens (aproximados: 1 token ~ 4 chars en español)
MAX_CHUNK_CHARS = 3000  # ~750 tokens
MIN_CHUNK_CHARS = 200   # ~50 tokens
OVERLAP_CHARS = 200     # Overlap entre chunks de un artículo largo


def chunkear_articulo(articulo: ArticuloParsed, norma_titulo: str) -> list[dict]:
    """Divide un artículo en chunks respetando su estructura.

    Si el artículo cabe en un solo chunk, lo deja entero.
    Si es muy largo, divide por párrafos o incisos con overlap.
    """
    texto = articulo.texto.strip()
    if not texto:
        return []

    # Metadata común para todos los chunks de este artículo
    metadata_base = {
        "norma_titulo": norma_titulo,
        "articulo_numero": articulo.numero,
        "path": articulo.path,
    }

    # Si cabe en un solo chunk, no dividir
    if len(texto) <= MAX_CHUNK_CHARS:
        return [
            {
                "texto": texto,
                "metadata": metadata_base,
                "tokens": _estimar_tokens(texto),
            }
        ]

    # Dividir en sub-chunks
    return _dividir_articulo_largo(texto, metadata_base)


def _dividir_articulo_largo(texto: str, metadata_base: dict) -> list[dict]:
    """Divide un artículo largo en chunks por párrafos o incisos."""
    # Intentar dividir por incisos (numerados o con letras)
    parrafos = _dividir_por_parrafos(texto)

    chunks = []
    chunk_actual = ""

    for parrafo in parrafos:
        # Si agregar este párrafo excede el límite, cerrar chunk actual
        if chunk_actual and len(chunk_actual) + len(parrafo) > MAX_CHUNK_CHARS:
            if len(chunk_actual) >= MIN_CHUNK_CHARS:
                chunks.append({
                    "texto": chunk_actual.strip(),
                    "metadata": {**metadata_base, "parte": len(chunks) + 1},
                    "tokens": _estimar_tokens(chunk_actual),
                })
            # Overlap: mantener las últimas líneas
            lineas = chunk_actual.split("\n")
            overlap = ""
            for linea in reversed(lineas):
                if len(overlap) + len(linea) < OVERLAP_CHARS:
                    overlap = linea + "\n" + overlap
                else:
                    break
            chunk_actual = overlap + parrafo + "\n"
        else:
            chunk_actual += parrafo + "\n"

    # Último chunk
    if chunk_actual.strip() and len(chunk_actual.strip()) >= MIN_CHUNK_CHARS:
        chunks.append({
            "texto": chunk_actual.strip(),
            "metadata": {**metadata_base, "parte": len(chunks) + 1},
            "tokens": _estimar_tokens(chunk_actual),
        })
    elif chunk_actual.strip() and chunks:
        # Agregar al último chunk si es muy corto
        chunks[-1]["texto"] += "\n" + chunk_actual.strip()
        chunks[-1]["tokens"] = _estimar_tokens(chunks[-1]["texto"])

    return chunks


def _dividir_por_parrafos(texto: str) -> list[str]:
    """Divide texto en párrafos semánticos (por doble salto de línea o incisos)."""
    # Primero intentar por doble salto de línea
    parrafos = texto.split("\n\n")

    # Si solo hay un bloque grande, dividir por salto simple
    if len(parrafos) == 1:
        parrafos = texto.split("\n")

    # Filtrar vacíos
    return [p.strip() for p in parrafos if p.strip()]


def _estimar_tokens(texto: str) -> int:
    """Estimación rápida de tokens (1 token ~ 4 chars en español)."""
    return len(texto) // 4
