"""Endpoint principal de chat con streaming SSE."""

import json
import logging
import time
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.db.session import get_db
from app.models.query_log import QueryLog
from app.orchestrator.pipeline import ejecutar_consulta
from app.utils.security import registrar_consulta, validar_pregunta, verificar_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    pregunta: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    respuesta: str
    citas: list[dict[str, Any]]
    datos_vivos: dict[str, Any] | None = None
    verificacion_pasada: bool


def _obtener_ip(request: Request) -> str:
    """Obtiene la IP real del cliente (soporta proxies)."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/chat")
async def chat(request: Request, body: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Procesa una pregunta y devuelve respuesta con streaming SSE."""
    ip = _obtener_ip(request)

    # Validar input
    error_input = validar_pregunta(body.pregunta)
    if error_input:
        async def error_gen():
            yield {"event": "error", "data": json.dumps(error_input, ensure_ascii=False)}
        return EventSourceResponse(error_gen())

    # Rate limiting
    error_rate = await verificar_rate_limit(ip, db)
    if error_rate:
        async def rate_gen():
            yield {"event": "error", "data": json.dumps(error_rate, ensure_ascii=False)}
        return EventSourceResponse(rate_gen())

    session_id = uuid.UUID(body.session_id) if body.session_id else uuid.uuid4()
    inicio = time.monotonic()

    async def generar_eventos():
        respuesta_completa = ""
        citas = []
        datos_vivos = {}
        verificacion = True

        try:
            async for evento in ejecutar_consulta(body.pregunta, db):
                if evento["tipo"] == "texto":
                    respuesta_completa += evento["contenido"]
                    yield {"event": "texto", "data": json.dumps(evento["contenido"], ensure_ascii=False)}

                elif evento["tipo"] == "cita":
                    citas.append(evento["contenido"])
                    yield {"event": "cita", "data": json.dumps(evento["contenido"], ensure_ascii=False)}

                elif evento["tipo"] == "dato_vivo":
                    datos_vivos.update(evento["contenido"])
                    yield {"event": "dato_vivo", "data": json.dumps(evento["contenido"], ensure_ascii=False)}

                elif evento["tipo"] == "verificacion":
                    verificacion = evento["contenido"]
                    yield {"event": "verificacion", "data": json.dumps(verificacion)}

                elif evento["tipo"] == "error":
                    yield {"event": "error", "data": json.dumps(evento["contenido"], ensure_ascii=False)}

            # Registrar consulta para rate limiting
            await registrar_consulta(ip, db)

            # Guardar log
            latencia_ms = int((time.monotonic() - inicio) * 1000)
            log = QueryLog(
                session_id=session_id,
                pregunta=body.pregunta,
                respuesta=respuesta_completa,
                citas=citas,
                datos_vivos=datos_vivos or None,
                verificacion_pasada=verificacion,
                latencia_ms=latencia_ms,
            )
            db.add(log)
            await db.commit()

            yield {"event": "fin", "data": ""}

        except Exception as e:
            logger.exception("Error procesando consulta: %s", e)
            yield {"event": "error", "data": json.dumps("Error interno al procesar la consulta. Intenta de nuevo.", ensure_ascii=False)}

    return EventSourceResponse(generar_eventos())


@router.post("/chat/sync", response_model=ChatResponse)
async def chat_sync(request: Request, body: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Versión síncrona (no streaming) para testing."""
    ip = _obtener_ip(request)

    error_input = validar_pregunta(body.pregunta)
    if error_input:
        return ChatResponse(respuesta=error_input, citas=[], verificacion_pasada=False)

    error_rate = await verificar_rate_limit(ip, db)
    if error_rate:
        return ChatResponse(respuesta=error_rate, citas=[], verificacion_pasada=False)

    inicio = time.monotonic()
    session_id = uuid.UUID(body.session_id) if body.session_id else uuid.uuid4()

    respuesta_completa = ""
    citas = []
    datos_vivos = {}
    verificacion = True

    async for evento in ejecutar_consulta(body.pregunta, db):
        if evento["tipo"] == "texto":
            respuesta_completa += evento["contenido"]
        elif evento["tipo"] == "cita":
            citas.append(evento["contenido"])
        elif evento["tipo"] == "dato_vivo":
            datos_vivos.update(evento["contenido"])
        elif evento["tipo"] == "verificacion":
            verificacion = evento["contenido"]

    await registrar_consulta(ip, db)

    latencia_ms = int((time.monotonic() - inicio) * 1000)
    log = QueryLog(
        session_id=session_id,
        pregunta=body.pregunta,
        respuesta=respuesta_completa,
        citas=citas,
        datos_vivos=datos_vivos or None,
        verificacion_pasada=verificacion,
        latencia_ms=latencia_ms,
    )
    db.add(log)
    await db.commit()

    return ChatResponse(
        respuesta=respuesta_completa,
        citas=citas,
        datos_vivos=datos_vivos or None,
        verificacion_pasada=verificacion,
    )
