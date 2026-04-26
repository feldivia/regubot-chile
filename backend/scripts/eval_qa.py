"""Script de evaluación con dataset dorado de Q&A."""

import asyncio
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.session import async_session  # noqa: E402
from app.orchestrator.pipeline import ejecutar_consulta  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GOLDEN_QA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "golden_qa.jsonl"


async def evaluar():
    """Ejecuta evaluación contra dataset dorado."""
    if not GOLDEN_QA_PATH.exists():
        logger.error("Dataset dorado no encontrado: %s", GOLDEN_QA_PATH)
        return

    resultados = []
    with open(GOLDEN_QA_PATH, encoding="utf-8") as f:
        for linea in f:
            caso = json.loads(linea)
            pregunta = caso["pregunta"]
            norma_esperada = caso.get("norma_esperada", "")

            logger.info("Evaluando: %s", pregunta)

            try:
                respuesta_completa = ""
                citas = []

                async with async_session() as db:
                    async for evento in ejecutar_consulta(pregunta, db):
                        if evento["tipo"] == "texto":
                            respuesta_completa += evento["contenido"]
                        elif evento["tipo"] == "cita":
                            citas.append(evento["contenido"])

                # Métricas básicas
                tiene_citas = len(citas) > 0
                cita_correcta = any(
                    norma_esperada.lower() in str(c).lower() for c in citas
                ) if norma_esperada else True

                resultados.append({
                    "pregunta": pregunta,
                    "respuesta": respuesta_completa[:200],
                    "tiene_citas": tiene_citas,
                    "cita_correcta": cita_correcta,
                    "num_citas": len(citas),
                })

            except Exception as e:
                logger.warning("Error evaluando: %s - %s", pregunta, e)
                resultados.append({
                    "pregunta": pregunta,
                    "error": str(e),
                })

    # Resumen
    total = len(resultados)
    con_citas = sum(1 for r in resultados if r.get("tiene_citas"))
    citas_correctas = sum(1 for r in resultados if r.get("cita_correcta"))
    errores = sum(1 for r in resultados if "error" in r)

    logger.info("=== Resultados de evaluación ===")
    logger.info("Total casos: %d", total)
    logger.info("Con citas: %d/%d (%.1f%%)", con_citas, total, con_citas / max(total, 1) * 100)
    logger.info("Citas correctas: %d/%d (%.1f%%)", citas_correctas, total, citas_correctas / max(total, 1) * 100)
    logger.info("Errores: %d", errores)


if __name__ == "__main__":
    asyncio.run(evaluar())
