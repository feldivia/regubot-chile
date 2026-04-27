"""Capa de verificación anti-alucinación: valida que las citas existan y sean vigentes."""

import logging
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Articulo, Norma

logger = logging.getLogger(__name__)

PATRON_CITA = re.compile(r"\[CITA:([a-f0-9\-]+)\]")


async def verificar_respuesta(
    respuesta: str,
    db: AsyncSession,
) -> dict:
    """Verifica todas las citas en una respuesta.

    Retorna:
        {
            "pasada": bool,
            "citas_verificadas": [...],
            "citas_fallidas": [...],
            "respuesta_limpia": str  # con citas inválidas removidas
        }
    """
    citas_ids = PATRON_CITA.findall(respuesta)

    if not citas_ids:
        return {
            "pasada": True,
            "citas_verificadas": [],
            "citas_fallidas": [],
            "respuesta_limpia": respuesta,
        }

    citas_verificadas = []
    citas_fallidas = []
    respuesta_limpia = respuesta

    for articulo_id in citas_ids:
        resultado = await _verificar_cita(articulo_id, db)

        if resultado["valida"]:
            citas_verificadas.append(resultado)
        else:
            citas_fallidas.append(resultado)
            # Remover cita inválida de la respuesta
            respuesta_limpia = respuesta_limpia.replace(f"[CITA:{articulo_id}]", "")

    pasada = len(citas_fallidas) == 0

    if not pasada:
        logger.warning(
            "Verificación fallida: %d/%d citas inválidas",
            len(citas_fallidas),
            len(citas_ids),
        )

    return {
        "pasada": pasada,
        "citas_verificadas": citas_verificadas,
        "citas_fallidas": citas_fallidas,
        "respuesta_limpia": respuesta_limpia,
    }


async def _verificar_cita(articulo_id: str, db: AsyncSession) -> dict:
    """Verifica una cita individual."""
    try:
        # Buscar artículo en DB
        stmt = (
            select(Articulo, Norma)
            .join(Norma, Articulo.norma_id == Norma.id)
            .where(Articulo.id == articulo_id)
        )
        result = await db.execute(stmt)
        row = result.first()

        if not row:
            return {
                "articulo_id": articulo_id,
                "valida": False,
                "razon": "Artículo no encontrado en la base de datos",
            }

        articulo, norma = row.Articulo, row.Norma

        # Verificar vigencia
        if not articulo.vigente:
            return {
                "articulo_id": articulo_id,
                "valida": False,
                "razon": "Artículo no vigente",
                "norma": f"{norma.tipo} {norma.numero}",
            }

        if norma.derogada:
            return {
                "articulo_id": articulo_id,
                "valida": False,
                "razon": "Norma derogada",
                "norma": f"{norma.tipo} {norma.numero}",
            }

        return {
            "articulo_id": articulo_id,
            "valida": True,
            "norma_tipo": norma.tipo,
            "norma_numero": norma.numero,
            "norma_titulo": norma.titulo,
            "articulo_numero": articulo.numero,
            "articulo_path": articulo.path,
            "url_oficial": norma.url_oficial,
            "organismo": norma.organismo,
            "texto": articulo.texto,
        }

    except Exception as e:
        logger.warning("Error verificando cita %s: %s", articulo_id, e)
        return {
            "articulo_id": articulo_id,
            "valida": False,
            "razon": f"Error de verificación: {e!s}",
        }
