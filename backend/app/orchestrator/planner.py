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
    respuesta_directa: str | None = None


def planificar_consulta(pregunta: str, intencion: Intencion) -> PlanConsulta:
    """Genera un plan de consulta basado en la intención clasificada."""

    if intencion.tipo == "saludo":
        return PlanConsulta(
            consultar_rag=False,
            respuesta_directa=(
                "¡Hola! Soy ReguBot, tu asistente de regulación financiera chilena. "
                "Puedo ayudarte con derechos del consumidor, tasas de interés, "
                "Ley Fintec, mercado de valores y sistemas de pago. ¿En qué puedo ayudarte?"
            ),
        )

    if intencion.tipo == "fuera_alcance":
        return PlanConsulta(
            consultar_rag=False,
            respuesta_directa=(
                "Lo siento, solo puedo ayudarte con regulación financiera chilena "
                "(derechos del consumidor, créditos, mercado de valores, Ley Fintec y sistemas de pago). "
                "Para otros temas, consulta a un profesional especializado."
            ),
        )

    return PlanConsulta(consultar_rag=True)
