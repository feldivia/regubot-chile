"""Clasificador de intención de la pregunta del usuario."""

import logging
import re

logger = logging.getLogger(__name__)

# Palabras clave para cada tipo de intención
KEYWORDS_NORMATIVA = [
    "ley", "norma", "artículo", "decreto", "regulación", "derecho", "obligación",
    "prohibido", "permitido", "legal", "ilegal", "sanción", "multa", "infracción",
    "circular", "ncg", "reglamento", "cmf", "sernac", "superintendencia",
    "consumidor", "reclamo", "contrato", "cláusula", "abusiva",
    "crédito", "hipotecario", "tarjeta", "cuenta", "banco", "financiero",
    "pensión", "afp", "apv", "fondo", "inversión", "seguro",
    "prepago", "pagar", "cobrar", "comisión", "interés", "mora",
]

KEYWORDS_DATO_VIVO = [
    "uf", "utm", "tpm", "tasa", "dólar", "ipc", "inflación",
    "sueldo mínimo", "tasa máxima", "convencional", "valor", "hoy",
    "actual", "cuánto", "precio", "cotización",
]

KEYWORDS_FUERA_ALCANCE = [
    "salud", "penal", "criminal", "divorcio", "custodia", "arriendo",
    "laboral", "despido", "accidente", "tránsito", "inmigración",
]


class Intencion:
    """Resultado del clasificador de intención."""

    def __init__(self, tipo: str, confianza: float, requiere_dato_vivo: bool = False, detalle: str = ""):
        self.tipo = tipo  # 'normativa', 'dato_vivo', 'mixto', 'fuera_alcance', 'saludo'
        self.confianza = confianza
        self.requiere_dato_vivo = requiere_dato_vivo
        self.detalle = detalle


def clasificar_intencion(pregunta: str) -> Intencion:
    """Clasifica la intención de una pregunta del usuario.

    Usa heurísticas basadas en keywords. Simple pero efectivo para V1.
    """
    pregunta_lower = pregunta.lower().strip()

    # Saludos simples
    if _es_saludo(pregunta_lower):
        return Intencion(tipo="saludo", confianza=0.95)

    # Fuera de alcance
    score_fuera = _score_keywords(pregunta_lower, KEYWORDS_FUERA_ALCANCE)
    if score_fuera > 0.3:
        return Intencion(tipo="fuera_alcance", confianza=score_fuera, detalle="tema_no_financiero")

    # Scores
    score_normativa = _score_keywords(pregunta_lower, KEYWORDS_NORMATIVA)
    score_dato_vivo = _score_keywords(pregunta_lower, KEYWORDS_DATO_VIVO)

    # Clasificar
    if score_dato_vivo > 0.3 and score_normativa > 0.2:
        return Intencion(
            tipo="mixto",
            confianza=max(score_normativa, score_dato_vivo),
            requiere_dato_vivo=True,
        )
    elif score_dato_vivo > score_normativa and score_dato_vivo > 0.2:
        return Intencion(
            tipo="dato_vivo",
            confianza=score_dato_vivo,
            requiere_dato_vivo=True,
        )
    elif score_normativa > 0.1:
        return Intencion(
            tipo="normativa",
            confianza=score_normativa,
            requiere_dato_vivo=False,
        )
    else:
        # Default: tratar como normativa (es lo más probable)
        return Intencion(
            tipo="normativa",
            confianza=0.5,
            requiere_dato_vivo=False,
        )


def _es_saludo(texto: str) -> bool:
    """Detecta si el texto es un saludo simple."""
    saludos = ["hola", "buenos días", "buenas tardes", "buenas noches", "hey", "qué tal"]
    return any(texto.startswith(s) for s in saludos) and len(texto.split()) <= 5


def _score_keywords(texto: str, keywords: list[str]) -> float:
    """Calcula score de coincidencia con keywords (0-1)."""
    matches = sum(1 for kw in keywords if kw in texto)
    if not matches:
        return 0.0
    # Normalizar: más matches = mayor confianza, con techo en 1.0
    return min(matches / 3, 1.0)
