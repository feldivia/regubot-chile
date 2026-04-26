"""Scraper para normativa del Banco Central de Chile."""

import logging

import httpx
from selectolax.parser import HTMLParser

from app.ingestion.base import BaseScraper, NormaRaw

logger = logging.getLogger(__name__)

BCCH_NORMATIVA_URL = "https://www.bcentral.cl/web/banco-central/normativa"


class BCChScraper(BaseScraper):
    """Scraper para normativa del Banco Central (Compendio de Normas Financieras)."""

    nombre = "bcch"

    async def obtener_normas(self, identificadores: list[str] | None = None) -> list[NormaRaw]:
        """Obtiene normativa del Banco Central."""
        normas = []
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.get(BCCH_NORMATIVA_URL)
            response.raise_for_status()

            html = HTMLParser(response.text)
            links = html.css("a[href*='normativa'], a[href*='compendio']")

            for link in links[:30]:
                href = link.attributes.get("href", "")
                texto = link.text(strip=True)

                if not texto or not href or len(texto) < 10:
                    continue

                try:
                    if not href.startswith("http"):
                        href = f"https://www.bcentral.cl{href}"

                    response = await client.get(href)
                    response.raise_for_status()
                    content_html = HTMLParser(response.text)
                    contenido = content_html.css_first("article, .content, main, body")

                    if contenido and len(contenido.text(strip=True)) > 100:
                        normas.append(
                            NormaRaw(
                                tipo="norma_bcch",
                                numero="",
                                titulo=texto,
                                organismo="BCCh",
                                url_oficial=href,
                                texto_completo=contenido.text(strip=True),
                            )
                        )
                except Exception:
                    self.logger.debug("Error obteniendo norma BCCh: %s", texto)

        self.logger.info("BCCh: %d normas obtenidas", len(normas))
        return normas

    async def verificar_cambios(self, hash_anterior: str, identificador: str) -> bool:
        return False
