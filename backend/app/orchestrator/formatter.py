"""Formateador: reemplaza [CITA:id] por tarjetas de trazabilidad."""

import logging
import re

logger = logging.getLogger(__name__)

PATRON_CITA = re.compile(r"\[CITA:([a-f0-9\-]+)\]")

DISCLAIMER = (
    "\n\n---\n"
    "**Aviso:** Esta información es orientativa y no constituye asesoría legal. "
    "Para asesoría personalizada, consulta a un abogado o acude a [SERNAC](https://www.sernac.cl)."
)


def formatear_respuesta(
    respuesta: str,
    citas_verificadas: list[dict],
    datos_vivos: dict | None = None,
) -> dict:
    """Formatea la respuesta final con tarjetas de cita y disclaimer.

    Retorna:
        {
            "texto": str,           # Respuesta con citas inline
            "citas": [...],         # Tarjetas de trazabilidad
            "datos_vivos": {...},   # Datos en vivo usados
            "disclaimer": str
        }
    """
    # Crear mapa de citas por ID
    mapa_citas = {c["articulo_id"]: c for c in citas_verificadas}

    # Reemplazar [CITA:id] por referencias numeradas
    citas_numeradas = []
    contador = [0]  # Usar lista para mutabilidad en closure

    def reemplazar_cita(match):
        articulo_id = match.group(1)
        cita = mapa_citas.get(articulo_id)
        if cita:
            contador[0] += 1
            num = contador[0]
            citas_numeradas.append({
                "numero": num,
                "norma": f"{cita.get('norma_tipo', '')} {cita.get('norma_numero', '')}",
                "titulo": cita.get("norma_titulo", ""),
                "articulo": f"Art. {cita.get('articulo_numero', 'N/A')}",
                "path": cita.get("articulo_path", ""),
                "url": cita.get("url_oficial", ""),
                "organismo": cita.get("organismo", ""),
            })
            return f" [{num}]"
        return ""

    texto_formateado = PATRON_CITA.sub(reemplazar_cita, respuesta)

    # Agregar disclaimer
    texto_formateado += DISCLAIMER

    return {
        "texto": texto_formateado,
        "citas": citas_numeradas,
        "datos_vivos": datos_vivos,
        "disclaimer": DISCLAIMER.strip(),
    }
