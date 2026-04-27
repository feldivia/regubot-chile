"""Generador de respuestas con Claude + tool use."""

import json
import logging
from pathlib import Path
from typing import AsyncGenerator

from app.config import settings
from app.orchestrator.live_data import obtener_dato_vivo
from app.utils.claude_client import get_claude_client

logger = logging.getLogger(__name__)

# Cargar prompt de sistema
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _cargar_prompt(nombre: str) -> str:
    """Carga un prompt desde archivo .md."""
    ruta = PROMPTS_DIR / nombre
    if ruta.exists():
        return ruta.read_text(encoding="utf-8")
    logger.warning("Prompt no encontrado: %s", nombre)
    return ""


# Tools disponibles para Claude
TOOLS_DATOS_VIVOS = [
    {
        "name": "obtener_uf",
        "description": "Obtiene el valor actual de la UF (Unidad de Fomento).",
        "input_schema": {
            "type": "object",
            "properties": {
                "fecha": {
                    "type": "string",
                    "description": "Fecha opcional en formato YYYY-MM-DD. Si no se especifica, retorna el valor de hoy.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "obtener_utm",
        "description": "Obtiene el valor actual de la UTM (Unidad Tributaria Mensual).",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "obtener_tmc",
        "description": "Obtiene la Tasa Máxima Convencional vigente.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tramo": {
                    "type": "string",
                    "description": "Tramo de la TMC (opcional).",
                }
            },
            "required": [],
        },
    },
    {
        "name": "obtener_tpm",
        "description": "Obtiene la Tasa de Política Monetaria vigente del Banco Central.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "obtener_dolar_observado",
        "description": "Obtiene el valor del dólar observado.",
        "input_schema": {
            "type": "object",
            "properties": {
                "fecha": {
                    "type": "string",
                    "description": "Fecha opcional en formato YYYY-MM-DD.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "obtener_ipc",
        "description": "Obtiene la variación del IPC (Índice de Precios al Consumidor).",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]

# Mapeo de tool names a tipos de datos vivos
TOOL_A_DATO = {
    "obtener_uf": "uf",
    "obtener_utm": "utm",
    "obtener_tmc": "tmc",
    "obtener_tpm": "tpm",
    "obtener_dolar_observado": "dolar",
    "obtener_ipc": "ipc",
}


async def generar_respuesta(
    pregunta: str,
    chunks: list[dict],
    datos_vivos: dict | None = None,
) -> AsyncGenerator[dict, None]:
    """Genera respuesta con Claude usando RAG + tool use.

    Yields eventos de tipo: texto, cita, dato_vivo, error
    """
    system_prompt = _cargar_prompt("system.md")
    if not system_prompt:
        system_prompt = _prompt_sistema_default()

    # Construir contexto con chunks recuperados
    contexto = _formatear_contexto(chunks)

    # Incluir datos vivos si los hay
    contexto_datos = ""
    if datos_vivos:
        contexto_datos = "\n\n## Datos en vivo disponibles\n"
        for tipo, dato in datos_vivos.items():
            if "error" not in dato:
                contexto_datos += f"- {tipo.upper()}: {dato.get('valor', 'N/D')} (fecha: {dato.get('fecha', 'N/D')}, fuente: {dato.get('fuente', 'N/D')})\n"

    mensajes = [
        {
            "role": "user",
            "content": f"## Contexto normativo recuperado\n{contexto}{contexto_datos}\n\n## Pregunta del usuario\n{pregunta}",
        }
    ]

    client = get_claude_client()

    try:
        # Crear mensaje con streaming
        async with client.messages.stream(
            model=settings.claude_model,
            max_tokens=4096,
            system=system_prompt,
            messages=mensajes,
            # Tools deshabilitados: datos en vivo requieren credenciales BCCh no configuradas
            # tools=TOOLS_DATOS_VIVOS,
        ) as stream:
            tool_name = None
            tool_input_json = ""

            async for event in stream:
                if event.type == "content_block_start":
                    if event.content_block.type == "tool_use":
                        tool_name = event.content_block.name
                        tool_input_json = ""

                elif event.type == "content_block_delta":
                    if hasattr(event.delta, "text"):
                        yield {"tipo": "texto", "contenido": event.delta.text}
                    elif hasattr(event.delta, "partial_json"):
                        tool_input_json += event.delta.partial_json

                elif event.type == "content_block_stop":
                    if tool_name:
                        # Ejecutar tool y enviar resultado
                        resultado_tool = await _ejecutar_tool(tool_name, tool_input_json)
                        if resultado_tool:
                            yield {"tipo": "dato_vivo", "contenido": resultado_tool}
                        tool_name = None
                        tool_input_json = ""

    except Exception as e:
        logger.exception("Error generando respuesta con Claude")
        yield {"tipo": "error", "contenido": f"Error generando respuesta: {e!s}"}


async def _ejecutar_tool(nombre: str, input_json: str) -> dict | None:
    """Ejecuta un tool call de datos en vivo."""
    tipo = TOOL_A_DATO.get(nombre)
    if not tipo:
        logger.warning("Tool no reconocido: %s", nombre)
        return None

    try:
        resultado = await obtener_dato_vivo(tipo)
        return {tipo: resultado}
    except Exception as e:
        logger.warning("Error ejecutando tool %s: %s", nombre, e)
        return None


def _formatear_contexto(chunks: list[dict]) -> str:
    """Formatea los chunks recuperados como contexto para Claude."""
    if not chunks:
        return "No se encontraron normas relevantes en la base de datos."

    partes = []
    for i, chunk in enumerate(chunks, 1):
        partes.append(
            f"### Fuente {i}: {chunk.get('norma_tipo', '')} {chunk.get('norma_numero', '')} - {chunk.get('norma_titulo', '')}\n"
            f"**Artículo:** {chunk.get('articulo_numero', 'N/A')} | "
            f"**Ubicación:** {chunk.get('articulo_path', 'N/A')}\n"
            f"**ID artículo:** {chunk.get('articulo_id', '')}\n"
            f"**URL:** {chunk.get('url_oficial', '')}\n\n"
            f"{chunk.get('texto', '')}\n"
        )

    return "\n---\n".join(partes)


def _prompt_sistema_default() -> str:
    """Prompt de sistema por defecto si no se encuentra el archivo."""
    return """Eres ReguBot, un asistente de regulación financiera chilena.

## Reglas
1. Solo cita normas del contexto entregado. Nunca inventes.
2. Lenguaje simple. Cita fuentes con [CITA:<articulo_id>].
3. Si no hay info, di "No tengo información sobre eso en mi base de datos."
4. No des asesoría legal. Máximo 4 párrafos.
5. Termina con: "Esta información es orientativa. Para asesoría legal, consulta a un abogado o acude a SERNAC."
"""
