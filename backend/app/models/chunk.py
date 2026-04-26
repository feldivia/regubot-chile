"""Modelo para chunks vectorizados usados en RAG."""

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, gen_uuid


class Chunk(Base):
    """Chunk de texto con embedding para búsqueda vectorial."""

    __tablename__ = "chunk"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    articulo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articulo.id", ondelete="CASCADE"), nullable=False
    )
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = mapped_column(Vector(3072))
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)
    tokens: Mapped[int | None] = mapped_column(Integer)

    articulo = relationship("Articulo", back_populates="chunks")
