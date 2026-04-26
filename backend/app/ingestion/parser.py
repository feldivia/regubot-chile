"""Parser normativo que preserva jerarquía: Ley > Título > Capítulo > Artículo."""

import logging
import re
from dataclasses import dataclass, field

from app.ingestion.base import NormaRaw

logger = logging.getLogger(__name__)


@dataclass
class ArticuloParsed:
    """Artículo parseado con su jerarquía."""

    numero: str
    path: str  # "Titulo II > Capitulo 3 > Art 17 B"
    texto: str
    orden: int


@dataclass
class NormaParsed:
    """Norma completamente parseada con su estructura."""

    tipo: str
    numero: str
    titulo: str
    organismo: str
    url_oficial: str
    fecha_publicacion: str | None
    hash_contenido: str
    articulos: list[ArticuloParsed] = field(default_factory=list)
    derogada: bool = False


def parsear_norma(raw: NormaRaw) -> NormaParsed:
    """Parsea una norma cruda y extrae su estructura jerárquica."""
    if raw.secciones:
        # Si el scraper ya extrajo secciones, usarlas directamente
        articulos = _desde_secciones(raw.secciones)
    else:
        # Parsear desde texto completo
        articulos = _desde_texto(raw.texto_completo)

    if not articulos:
        logger.warning(
            "No se encontraron artículos en %s %s. Usando texto completo como único artículo.",
            raw.tipo,
            raw.numero,
        )
        articulos = [
            ArticuloParsed(
                numero="completo",
                path=f"{raw.titulo}",
                texto=raw.texto_completo,
                orden=0,
            )
        ]

    logger.info(
        "Parseada %s %s: %d artículos extraídos",
        raw.tipo,
        raw.numero,
        len(articulos),
    )

    return NormaParsed(
        tipo=raw.tipo,
        numero=raw.numero,
        titulo=raw.titulo,
        organismo=raw.organismo,
        url_oficial=raw.url_oficial,
        fecha_publicacion=raw.fecha_publicacion,
        hash_contenido=raw.hash_contenido,
        articulos=articulos,
        derogada=raw.derogada,
    )


def _desde_secciones(secciones: list[dict]) -> list[ArticuloParsed]:
    """Convierte secciones del scraper en artículos parseados."""
    articulos = []
    for i, seccion in enumerate(secciones):
        texto = seccion.get("texto", "").strip()
        if not texto:
            continue

        articulos.append(
            ArticuloParsed(
                numero=seccion.get("numero", str(i + 1)),
                path=seccion.get("path", ""),
                texto=texto,
                orden=i,
            )
        )
    return articulos


def _desde_texto(texto: str) -> list[ArticuloParsed]:
    """Parsea artículos desde texto plano usando regex."""
    # Patrón para detectar artículos
    patron = re.compile(
        r"(Art[íi]culo|Art\.?)\s+(\d+[\w\s°]*?)[\.\-\s]",
        re.IGNORECASE | re.MULTILINE,
    )

    matches = list(patron.finditer(texto))
    if not matches:
        return []

    articulos = []
    path_actual = _detectar_path_inicial(texto)

    for i, match in enumerate(matches):
        inicio = match.start()
        fin = matches[i + 1].start() if i + 1 < len(matches) else len(texto)

        texto_articulo = texto[inicio:fin].strip()
        numero = match.group(2).strip().rstrip(".-")

        # Actualizar path si hay encabezados entre artículos
        if i > 0:
            texto_entre = texto[matches[i - 1].end() : inicio]
            nuevo_path = _actualizar_path(path_actual, texto_entre)
            if nuevo_path:
                path_actual = nuevo_path

        articulos.append(
            ArticuloParsed(
                numero=numero,
                path=f"{path_actual} > Art {numero}" if path_actual else f"Art {numero}",
                texto=texto_articulo,
                orden=i,
            )
        )

    return articulos


def _detectar_path_inicial(texto: str) -> str:
    """Detecta el path jerárquico inicial del texto."""
    lineas = texto[:2000].split("\n")
    partes = []

    for linea in lineas:
        linea = linea.strip().upper()
        if re.match(r"^T[ÍI]TULO\s+", linea):
            partes = [linea.strip()[:100]]
        elif re.match(r"^CAP[ÍI]TULO\s+", linea):
            partes = partes[:1] + [linea.strip()[:100]]
        elif re.match(r"^ART", linea):
            break

    return " > ".join(partes)


def _actualizar_path(path_actual: str, texto_entre: str) -> str | None:
    """Busca encabezados en texto intermedio y actualiza el path."""
    for linea in texto_entre.split("\n"):
        linea = linea.strip()
        upper = linea.upper()
        if re.match(r"^T[ÍI]TULO\s+", upper):
            return linea[:100]
        if re.match(r"^CAP[ÍI]TULO\s+", upper):
            partes = path_actual.split(" > ")
            return f"{partes[0]} > {linea[:100]}" if partes else linea[:100]
    return None
