"""Entrypoint de la aplicación FastAPI."""

import logging
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin import router as admin_router
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.config import settings
from app.db.session import engine
from app.models.base import Base

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa recursos al arrancar y los libera al parar."""
    # Configurar logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    # Sentry (si configurado)
    if settings.sentry_dsn:
        sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=0.1)

    # Habilitar extensión pgvector y crear tablas
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

    logger.info("RegBot Chile iniciado correctamente")
    yield

    # Cleanup
    await engine.dispose()
    logger.info("RegBot Chile detenido")


app = FastAPI(
    title="RegBot Chile",
    description="API del chatbot de regulación financiera chilena",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS para el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.up.railway.app",
        "https://*.railway.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(health_router)
app.include_router(chat_router, prefix="/api")
app.include_router(admin_router, prefix="/api/admin")
