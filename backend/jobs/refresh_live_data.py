"""Job de refresh de datos en vivo (UF, TMC, etc.)."""

import logging

from app.orchestrator.live_data import obtener_dato_vivo

logger = logging.getLogger(__name__)

DATOS_A_REFRESCAR = ["uf", "utm", "tpm", "dolar", "ipc", "tmc"]


async def refrescar_datos_vivos():
    """Refresca todos los datos en vivo en el cache."""
    logger.info("Iniciando refresh de datos en vivo")
    for tipo in DATOS_A_REFRESCAR:
        try:
            resultado = await obtener_dato_vivo(tipo)
            if "error" in resultado:
                logger.warning("Error refrescando %s: %s", tipo, resultado["error"])
            else:
                logger.info("Refrescado %s: %s", tipo, resultado.get("valor", "N/D"))
        except Exception:
            logger.exception("Error refrescando %s", tipo)
