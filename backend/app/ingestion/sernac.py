"""Scraper selectivo para SERNAC."""

import logging

import httpx
from selectolax.parser import HTMLParser

from app.ingestion.base import BaseScraper, NormaRaw

logger = logging.getLogger(__name__)

SERNAC_URL = "https://www.sernac.cl/portal/619/w3-propertyvalue-76016.html"


class SERNACScraper(BaseScraper):
    """Scraper selectivo para contenido regulatorio de SERNAC."""

    nombre = "sernac"

    async def obtener_normas(self, identificadores: list[str] | None = None) -> list[NormaRaw]:
        """Obtiene contenido regulatorio de SERNAC."""
        normas = []
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            try:
                response = await client.get(SERNAC_URL)
                response.raise_for_status()
                html = HTMLParser(response.text)
                links = html.css("a[href*='articulo'], a[href*='normativa'], a[href*='derechos']")

                for link in links[:20]:
                    href = link.attributes.get("href", "")
                    texto = link.text(strip=True)

                    if not texto or not href:
                        continue

                    if not href.startswith("http"):
                        href = f"https://www.sernac.cl{href}"

                    try:
                        resp = await client.get(href)
                        resp.raise_for_status()
                        content = HTMLParser(resp.text)
                        body = content.css_first("article, .content, main")

                        if body and len(body.text(strip=True)) > 100:
                            normas.append(
                                NormaRaw(
                                    tipo="guia_sernac",
                                    numero="",
                                    titulo=texto,
                                    organismo="SERNAC",
                                    url_oficial=href,
                                    texto_completo=body.text(strip=True),
                                )
                            )
                    except Exception:
                        self.logger.debug("Error obteniendo contenido SERNAC: %s", texto)

            except Exception:
                self.logger.exception("Error accediendo a SERNAC")

        self.logger.info("SERNAC: %d documentos obtenidos", len(normas))
        return normas

    async def verificar_cambios(self, hash_anterior: str, identificador: str) -> bool:
        return False
