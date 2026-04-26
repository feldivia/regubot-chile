"""Modelo para log de consultas (auditoría y mejora continua)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, gen_uuid


class QueryLog(Base):
    """Registro de cada consulta para auditoría."""

    __tablename__ = "query_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    session_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    pregunta: Mapped[str] = mapped_column(Text, nullable=False)
    respuesta: Mapped[str] = mapped_column(Text, nullable=False)
    citas: Mapped[dict | None] = mapped_column(JSONB)
    datos_vivos: Mapped[dict | None] = mapped_column(JSONB)
    verificacion_pasada: Mapped[bool | None] = mapped_column(Boolean)
    latencia_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
