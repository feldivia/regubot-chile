"""Modelo para rate limiting por IP."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, gen_uuid


class RateLimit(Base):
    """Registro de consultas por IP para rate limiting."""

    __tablename__ = "rate_limit"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    ip: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    consultas_hoy: Mapped[int] = mapped_column(Integer, default=1)
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
