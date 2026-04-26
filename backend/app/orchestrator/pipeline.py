"""Pipeline principal del orquestador: une todas las piezas."""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.orchestrator.formatter import formatear_respuesta
from app.orchestrator.generator import generar_respuesta
from app.orchestrator.intent import clasificar_intencion
from app.orchestrator.live_data import obtener_multiples_datos
from app.orchestrator.planner import planificar_consulta
from app.orchestrator.retriever import recuperar_chunks
from app.orchestrator.verifier import verificar_respuesta

logger = logging.getLogger(__name__)


async def ejecutar_consulta(
    pregunta: str,
    db: AsyncSession,
) -> AsyncGenerator[dict, None]:
    """Ejecuta el pipeline completo de una consulta.

    Yields eventos de streaming:
        {"tipo": "texto", "contenido": "..."}
        {"tipo": "cita", "contenido": {...}}
        {"tipo": "dato_vivo", "contenido": {...}}
        {"tipo": "verificacion", "contenido": bool}
        {"tipo": "error", "contenido": "..."}
    """
    # 1. Clasificar intención
    intencion = clasificar_intencion(pregunta)
    logger.info("Intención: %s (confianza: %.2f)", intencion.tipo, intencion.confianza)

    # 2. Planificar consulta
    plan = planificar_consulta(pregunta, intencion)

    # Respuesta directa (saludos, fuera de alcance)
    if plan.respuesta_directa:
        yield {"tipo": "texto", "contenido": plan.respuesta_directa}
        return

    # 3. Recuperar contexto (RAG + datos vivos en paralelo)
    chunks = []
    datos_vivos = {}

    if plan.consultar_rag:
        try:
            chunks = await recuperar_chunks(pregunta, db, filtros=plan.filtros_rag)
        except Exception as e:
            logger.warning("Error en retrieval: %s", e)

    if plan.consultar_datos_vivos:
        try:
            datos_vivos = await obtener_multiples_datos(plan.datos_vivos_requeridos)
            for tipo, dato in datos_vivos.items():
                yield {"tipo": "dato_vivo", "contenido": {tipo: dato}}
        except Exception as e:
            logger.warning("Error obteniendo datos vivos: %s", e)

    # 4. Generar respuesta con Claude
    respuesta_completa = ""
    async for evento in generar_respuesta(pregunta, chunks, datos_vivos):
        if evento["tipo"] == "texto":
            respuesta_completa += evento["contenido"]
            yield evento
        elif evento["tipo"] == "dato_vivo":
            datos_vivos.update(evento["contenido"])
            yield evento
        elif evento["tipo"] == "error":
            yield evento
            return

    # 5. Verificar citas
    try:
        verificacion = await verificar_respuesta(respuesta_completa, db)
        yield {"tipo": "verificacion", "contenido": verificacion["pasada"]}

        # 6. Formatear con tarjetas de trazabilidad
        formateado = formatear_respuesta(
            verificacion["respuesta_limpia"],
            verificacion["citas_verificadas"],
            datos_vivos,
        )

        # Emitir citas como eventos
        for cita in formateado["citas"]:
            yield {"tipo": "cita", "contenido": cita}

    except Exception as e:
        logger.warning("Error en verificación/formateo: %s", e)
        yield {"tipo": "verificacion", "contenido": False}
