"""Endpoint principal de chat con streaming SSE."""

import json
import logging
import time
import uuid
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.db.session import get_db
from app.models.query_log import QueryLog
from app.orchestrator.pipeline import ejecutar_consulta

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


@router.post("/chat")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Procesa una pregunta y devuelve respuesta con streaming SSE."""
    session_id = uuid.UUID(request.session_id) if request.session_id else uuid.uuid4()
    inicio = time.monotonic()

    async def generar_eventos():
        respuesta_completa = ""
        citas = []
        datos_vivos = {}
        verificacion = True

        try:
            async for evento in ejecutar_consulta(request.pregunta, db):
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

            # Guardar log de consulta
            latencia_ms = int((time.monotonic() - inicio) * 1000)
            log = QueryLog(
                session_id=session_id,
                pregunta=request.pregunta,
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
            logger.exception("Error procesando consulta")
            yield {"event": "error", "data": f"Error interno: {e!s}"}

    return EventSourceResponse(generar_eventos())


@router.post("/chat/sync", response_model=ChatResponse)
async def chat_sync(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Versión síncrona (no streaming) para testing."""
    inicio = time.monotonic()
    session_id = uuid.UUID(request.session_id) if request.session_id else uuid.uuid4()

    respuesta_completa = ""
    citas = []
    datos_vivos = {}
    verificacion = True

    async for evento in ejecutar_consulta(request.pregunta, db):
        if evento["tipo"] == "texto":
            respuesta_completa += evento["contenido"]
        elif evento["tipo"] == "cita":
            citas.append(evento["contenido"])
        elif evento["tipo"] == "dato_vivo":
            datos_vivos.update(evento["contenido"])
        elif evento["tipo"] == "verificacion":
            verificacion = evento["contenido"]

    latencia_ms = int((time.monotonic() - inicio) * 1000)
    log = QueryLog(
        session_id=session_id,
        pregunta=request.pregunta,
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
