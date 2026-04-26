"""Configuración de APScheduler para jobs programados."""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def configurar_scheduler():
    """Configura todos los jobs programados."""
    from jobs.refresh_live_data import refrescar_datos_vivos
    from jobs.reindex_daily import reindexar_corpus

    # Refresh de datos en vivo cada hora
    scheduler.add_job(
        refrescar_datos_vivos,
        IntervalTrigger(hours=1),
        id="refresh_datos_vivos",
        name="Refrescar datos en vivo",
        replace_existing=True,
    )

    # Reindexación diaria a las 3 AM
    scheduler.add_job(
        reindexar_corpus,
        CronTrigger(hour=3, minute=0),
        id="reindex_diario",
        name="Reindexación diaria del corpus",
        replace_existing=True,
    )

    logger.info("Scheduler configurado con %d jobs", len(scheduler.get_jobs()))


def iniciar_scheduler():
    """Inicia el scheduler."""
    configurar_scheduler()
    scheduler.start()
    logger.info("Scheduler iniciado")


def detener_scheduler():
    """Detiene el scheduler."""
    scheduler.shutdown()
    logger.info("Scheduler detenido")
