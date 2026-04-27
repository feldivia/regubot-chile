"""Query planner: decide qué fuentes consultar según la intención."""

import logging
from dataclasses import dataclass, field

from app.orchestrator.intent import Intencion

logger = logging.getLogger(__name__)


@dataclass
class PlanConsulta:
    """Plan de ejecución para una consulta."""

    consultar_rag: bool = True
    consultar_datos_vivos: bool = False
    datos_vivos_requeridos: list[str] = field(default_factory=list)
    filtros_rag: dict = field(default_factory=dict)
    respuesta_directa: str | None = None  # Para saludos o fuera de alcance


# Mapeo de keywords a datos vivos específicos
MAPEO_DATOS_VIVOS = {
    "uf": "uf",
    "unidad de fomento": "uf",
    "utm": "utm",
    "unidad tributaria": "utm",
    "tpm": "tpm",
    "tasa política monetaria": "tpm",
    "tasa máxima": "tmc",
    "convencional": "tmc",
    "tmc": "tmc",
    "dólar": "dolar",
    "dollar": "dolar",
    "ipc": "ipc",
    "inflación": "ipc",
    "sueldo mínimo": "sueldo_minimo",
    "salario mínimo": "sueldo_minimo",
    "ingreso mínimo": "sueldo_minimo",
}


def planificar_consulta(pregunta: str, intencion: Intencion) -> PlanConsulta:
    """Genera un plan de consulta basado en la intención clasificada."""
    pregunta_lower = pregunta.lower()

    if intencion.tipo == "saludo":
        return PlanConsulta(
            consultar_rag=False,
            respuesta_directa=(
                "¡Hola! Soy ReguBot, tu asistente de regulación financiera chilena. "
                "Puedo ayudarte con preguntas sobre derechos del consumidor, tasas de interés, "
                "Ley Fintec, mercado de valores y sistemas de pago. ¿En qué puedo ayudarte?"
            ),
        )

    if intencion.tipo == "fuera_alcance":
        return PlanConsulta(
            consultar_rag=False,
            respuesta_directa=(
                "Lo siento, mi especialidad es la regulación financiera chilena. "
                "No puedo ayudarte con temas fuera de ese ámbito. "
                "Para otros temas legales, te recomiendo consultar a un profesional especializado."
            ),
        )

    # Determinar qué datos vivos se necesitan
    datos_requeridos = []
    if intencion.requiere_dato_vivo:
        for keyword, dato in MAPEO_DATOS_VIVOS.items():
            if keyword in pregunta_lower and dato not in datos_requeridos:
                datos_requeridos.append(dato)

        # Si mencionó datos vivos pero no detectamos cuál, pedir los más comunes
        if not datos_requeridos:
            datos_requeridos = ["uf"]

    # Filtros RAG por organismo si se detectan
    filtros = {}
    if "cmf" in pregunta_lower:
        filtros["organismo"] = "CMF"
    elif "sii" in pregunta_lower or "impuesto" in pregunta_lower:
        filtros["organismo"] = "SII"
    elif "pensión" in pregunta_lower or "afp" in pregunta_lower:
        filtros["organismo"] = "Congreso"  # DL 3500

    return PlanConsulta(
        consultar_rag=True,
        consultar_datos_vivos=bool(datos_requeridos),
        datos_vivos_requeridos=datos_requeridos,
        filtros_rag=filtros,
    )
