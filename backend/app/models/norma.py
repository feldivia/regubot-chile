"""Modelos para normas jurídicas y sus relaciones."""

import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, gen_uuid


class Norma(Base, TimestampMixin):
    """Norma jurídica (ley, decreto, NCG, circular)."""

    __tablename__ = "norma"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    numero: Mapped[str | None] = mapped_column(String(50))
    titulo: Mapped[str] = mapped_column(Text, nullable=False)
    organismo: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha_publicacion: Mapped[date | None] = mapped_column(Date)
    fecha_vigencia: Mapped[date | None] = mapped_column(Date)
    derogada: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_derogacion: Mapped[date | None] = mapped_column(Date)
    url_oficial: Mapped[str] = mapped_column(Text, nullable=False)
    hash_contenido: Mapped[str] = mapped_column(String(64), nullable=False)

    articulos: Mapped[list["Articulo"]] = relationship(
        back_populates="norma", cascade="all, delete-orphan"
    )


class Articulo(Base):
    """Artículo o sección estructural de una norma."""

    __tablename__ = "articulo"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    norma_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("norma.id", ondelete="CASCADE"), nullable=False
    )
    path: Mapped[str] = mapped_column(Text, nullable=False)
    numero: Mapped[str | None] = mapped_column(String(20))
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    vigente: Mapped[bool] = mapped_column(Boolean, default=True)

    norma: Mapped["Norma"] = relationship(back_populates="articulos")
    chunks: Mapped[list["Chunk"]] = relationship(  # noqa: F821
        back_populates="articulo", cascade="all, delete-orphan"
    )


class RelacionNorma(Base):
    """Relación entre normas (modifica, deroga, reglamenta, cita)."""

    __tablename__ = "relacion_norma"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    norma_origen: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("norma.id"), nullable=False
    )
    norma_destino: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("norma.id"), nullable=False
    )
    tipo_relacion: Mapped[str] = mapped_column(String(20), nullable=False)
