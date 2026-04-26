"""Generación de embeddings con OpenAI (text-embedding-3-large)."""

import logging

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    """Singleton del cliente async de OpenAI."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def generar_embeddings(textos: list[str]) -> list[list[float]]:
    """Genera embeddings para una lista de textos usando OpenAI."""
    if not textos:
        return []

    # Procesar en lotes de 2048 (límite de OpenAI)
    embeddings: list[list[float]] = []
    batch_size = 2048

    for i in range(0, len(textos), batch_size):
        lote = textos[i : i + batch_size]
        lote_embeddings = await _llamar_openai(lote)
        embeddings.extend(lote_embeddings)

    return embeddings


async def _llamar_openai(textos: list[str]) -> list[list[float]]:
    """Llama a la API de OpenAI para obtener embeddings."""
    client = _get_client()
    response = await client.embeddings.create(
        input=textos,
        model=settings.embedding_model,
        dimensions=settings.embedding_dimensions,
    )
    return [item.embedding for item in response.data]


async def generar_embedding_query(texto: str) -> list[float]:
    """Genera embedding para una query de búsqueda."""
    client = _get_client()
    response = await client.embeddings.create(
        input=[texto],
        model=settings.embedding_model,
        dimensions=settings.embedding_dimensions,
    )
    return response.data[0].embedding
