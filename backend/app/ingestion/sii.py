"""Scraper para SII (Servicio de Impuestos Internos)."""

import logging

import httpx
from selectolax.parser import HTMLParser

from app.ingestion.base import BaseScraper, NormaRaw

logger = logging.getLogger(__name__)

SII_NORMATIVA_URL = "https://www.sii.cl/normativa_legislacion/"


class SIIScraper(BaseScraper):
    """Scraper para normativa del SII."""

    nombre = "sii"

    async def obtener_normas(self, identificadores: list[str] | None = None) -> list[NormaRaw]:
        """Obtiene normativa del SII."""
        normas = []
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.get(SII_NORMATIVA_URL)
            response.raise_for_status()

            html = HTMLParser(response.text)
            # Buscar links a circulares y resoluciones
            links = html.css("a[href*='circular'], a[href*='resolucion']")

            for link in links[:50]:  # Limitar en V1
                href = link.attributes.get("href", "")
                texto = link.text(strip=True)

                if not texto or not href:
                    continue

                try:
                    if not href.startswith("http"):
                        href = f"https://www.sii.cl{href}"

                    response = await client.get(href)
                    response.raise_for_status()
                    content_html = HTMLParser(response.text)
                    contenido = content_html.css_first(".field-item, .content, article, body")

                    if contenido and len(contenido.text(strip=True)) > 100:
                        normas.append(
                            NormaRaw(
                                tipo="circular",
                                numero="",
                                titulo=texto,
                                organismo="SII",
                                url_oficial=href,
                                texto_completo=contenido.text(strip=True),
                            )
                        )
                except Exception:
                    self.logger.debug("Error obteniendo norma SII: %s", texto)

        self.logger.info("SII: %d normas obtenidas", len(normas))
        return normas

    async def verificar_cambios(self, hash_anterior: str, identificador: str) -> bool:
        return False
