"""Clase base abstracta para scrapers de fuentes normativas."""

import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class NormaRaw:
    """Representación cruda de una norma antes de parsear."""

    tipo: str  # 'ley', 'decreto', 'ncg', 'circular'
    numero: str
    titulo: str
    organismo: str
    url_oficial: str
    fecha_publicacion: str | None = None
    texto_completo: str = ""
    secciones: list[dict] = field(default_factory=list)
    derogada: bool = False

    @property
    def hash_contenido(self) -> str:
        return hashlib.sha256(self.texto_completo.encode()).hexdigest()


class BaseScraper(ABC):
    """Clase base para todos los scrapers. Garantiza idempotencia."""

    nombre: str = "base"

    def __init__(self):
        self.logger = logging.getLogger(f"scraper.{self.nombre}")

    @abstractmethod
    async def obtener_normas(self, identificadores: list[str] | None = None) -> list[NormaRaw]:
        """Obtiene las normas de la fuente. Si se pasan identificadores, solo esas."""
        ...

    @abstractmethod
    async def verificar_cambios(self, hash_anterior: str, identificador: str) -> bool:
        """Verifica si una norma ha cambiado comparando hashes."""
        ...
