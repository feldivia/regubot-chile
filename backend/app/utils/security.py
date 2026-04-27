"""Seguridad: rate limiting por IP, validación de input, anti prompt injection."""

import logging
import re
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rate_limit import RateLimit

logger = logging.getLogger(__name__)

MAX_CONSULTAS_POR_DIA = 3
MAX_PALABRAS = 30

# Patrones de prompt injection
PATRONES_INJECTION = [
    r"ignora\s+(las\s+)?instrucciones",
    r"ignore\s+(your\s+)?instructions",
    r"olvida\s+(todo|las\s+reglas)",
    r"forget\s+(everything|your\s+rules)",
    r"act\s+as\s+",
    r"actua\s+como\s+",
    r"pretend\s+(you\s+are|to\s+be)",
    r"finge\s+(que\s+eres|ser)",
    r"system\s*prompt",
    r"nueva\s+instrucción",
    r"new\s+instruction",
    r"jailbreak",
    r"DAN\s+mode",
    r"developer\s+mode",
    r"bypass",
    r"\[system\]",
    r"\[INST\]",
    r"<\|im_start\|>",
    r"<system>",
]

_REGEX_INJECTION = re.compile("|".join(PATRONES_INJECTION), re.IGNORECASE)


def validar_pregunta(pregunta: str) -> str | None:
    """Valida la pregunta del usuario. Retorna mensaje de error o None si es válida."""
    texto = pregunta.strip()

    if not texto:
        return "La pregunta no puede estar vacía."

    if len(texto) < 3:
        return "La pregunta es demasiado corta."

    palabras = texto.split()
    if len(palabras) > MAX_PALABRAS:
        return f"La pregunta es demasiado larga. Máximo {MAX_PALABRAS} palabras."

    if _REGEX_INJECTION.search(texto):
        logger.warning("Prompt injection detectado: %s", texto[:100])
        return "La consulta no es válida."

    return None


async def verificar_rate_limit(ip: str, db: AsyncSession) -> str | None:
    """Verifica si la IP puede hacer más consultas. Retorna error o None si OK."""
    ahora = datetime.now(timezone.utc)
    hace_24h = ahora - timedelta(hours=24)

    # Contar consultas de esta IP en las últimas 24 horas
    stmt = select(func.count(RateLimit.id)).where(
        and_(
            RateLimit.ip == ip,
            RateLimit.fecha >= hace_24h,
        )
    )
    count = await db.scalar(stmt) or 0

    if count >= MAX_CONSULTAS_POR_DIA:
        # Calcular cuándo se libera la próxima consulta
        stmt_oldest = (
            select(RateLimit.fecha)
            .where(and_(RateLimit.ip == ip, RateLimit.fecha >= hace_24h))
            .order_by(RateLimit.fecha.asc())
            .limit(1)
        )
        oldest = await db.scalar(stmt_oldest)
        if oldest:
            libera = oldest + timedelta(hours=24)
            horas_restantes = max(1, int((libera - ahora).total_seconds() / 3600))
            return f"Has alcanzado el límite de {MAX_CONSULTAS_POR_DIA} consultas diarias. Podrás volver a preguntar en {horas_restantes} hora{'s' if horas_restantes > 1 else ''}."

        return f"Has alcanzado el límite de {MAX_CONSULTAS_POR_DIA} consultas diarias."

    return None


async def registrar_consulta(ip: str, db: AsyncSession) -> None:
    """Registra una consulta para esta IP."""
    registro = RateLimit(ip=ip)
    db.add(registro)
