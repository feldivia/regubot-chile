"""Scraper para CMF (Comisión para el Mercado Financiero)."""

import logging
import re

import httpx
from selectolax.parser import HTMLParser

from app.ingestion.base import BaseScraper, NormaRaw

logger = logging.getLogger(__name__)

CMF_NORMATIVA_URL = "https://www.cmfchile.cl/portal/principal/613/w3-propertyvalue-18405.html"


class CMFScraper(BaseScraper):
    """Scraper para normativa de la CMF (NCGs, circulares)."""

    nombre = "cmf"

    async def obtener_normas(self, identificadores: list[str] | None = None) -> list[NormaRaw]:
        """Obtiene normas de la CMF."""
        normas = []
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.get(CMF_NORMATIVA_URL)
            response.raise_for_status()

            html = HTMLParser(response.text)
            links = html.css("a[href*='normativa']")

            for link in links:
                href = link.attributes.get("href", "")
                texto = link.text(strip=True)

                if not texto or not href:
                    continue

                # Filtrar por identificadores si se especifican
                if identificadores:
                    if not any(ident in texto for ident in identificadores):
                        continue

                try:
                    norma = await self._obtener_norma_cmf(client, href, texto)
                    if norma:
                        normas.append(norma)
                except Exception:
                    self.logger.exception("Error obteniendo norma CMF: %s", texto)

        self.logger.info("CMF: %d normas obtenidas", len(normas))
        return normas

    async def _obtener_norma_cmf(
        self, client: httpx.AsyncClient, url: str, titulo: str
    ) -> NormaRaw | None:
        """Obtiene una norma específica de la CMF."""
        if not url.startswith("http"):
            url = f"https://www.cmfchile.cl{url}"

        response = await client.get(url)
        response.raise_for_status()
        html = HTMLParser(response.text)

        contenido = html.css_first(".field-item, .content, article")
        if not contenido:
            return None

        texto = contenido.text(strip=True)
        if len(texto) < 50:
            return None

        # Extraer número de NCG o circular
        numero_match = re.search(r"(NCG|Circular)\s*[Nn]?[°º.]?\s*(\d+)", titulo)
        numero = numero_match.group(2) if numero_match else ""
        tipo = "ncg" if "NCG" in titulo.upper() else "circular"

        return NormaRaw(
            tipo=tipo,
            numero=numero,
            titulo=titulo,
            organismo="CMF",
            url_oficial=url,
            texto_completo=texto,
        )

    async def verificar_cambios(self, hash_anterior: str, identificador: str) -> bool:
        """Verifica cambios en una norma de la CMF."""
        return False  # TODO: implementar verificación de cambios
