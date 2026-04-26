"""Scraper para Superintendencia de Pensiones."""

import logging

import httpx
from selectolax.parser import HTMLParser

from app.ingestion.base import BaseScraper, NormaRaw

logger = logging.getLogger(__name__)

SP_URL = "https://www.spensiones.cl/portal/institucional/594/w3-propertyvalue-6114.html"


class SPScraper(BaseScraper):
    """Scraper para normativa de la Superintendencia de Pensiones."""

    nombre = "sp"

    async def obtener_normas(self, identificadores: list[str] | None = None) -> list[NormaRaw]:
        """Obtiene normativa de la SP."""
        normas = []
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            try:
                response = await client.get(SP_URL)
                response.raise_for_status()
                html = HTMLParser(response.text)
                links = html.css("a[href*='norma'], a[href*='circular']")

                for link in links[:30]:
                    href = link.attributes.get("href", "")
                    texto = link.text(strip=True)

                    if not texto or not href:
                        continue

                    if not href.startswith("http"):
                        href = f"https://www.spensiones.cl{href}"

                    try:
                        resp = await client.get(href)
                        resp.raise_for_status()
                        content = HTMLParser(resp.text)
                        body = content.css_first("article, .content, main, body")

                        if body and len(body.text(strip=True)) > 100:
                            normas.append(
                                NormaRaw(
                                    tipo="norma_sp",
                                    numero="",
                                    titulo=texto,
                                    organismo="SP",
                                    url_oficial=href,
                                    texto_completo=body.text(strip=True),
                                )
                            )
                    except Exception:
                        self.logger.debug("Error obteniendo norma SP: %s", texto)

            except Exception:
                self.logger.exception("Error accediendo a SP")

        self.logger.info("SP: %d normas obtenidas", len(normas))
        return normas

    async def verificar_cambios(self, hash_anterior: str, identificador: str) -> bool:
        return False
