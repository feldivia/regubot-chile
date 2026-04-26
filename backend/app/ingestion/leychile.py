"""Scraper para leychile.cl (Biblioteca del Congreso Nacional)."""

import logging
import re

import httpx
from selectolax.parser import HTMLParser

from app.ingestion.base import BaseScraper, NormaRaw

logger = logging.getLogger(__name__)

# Leyes prioritarias V1 con sus IDs en leychile.cl
LEYES_PRIORITARIAS = {
    "19496": {"titulo": "Protección del Consumidor", "organismo": "Congreso"},
    "21521": {"titulo": "Ley Fintec", "organismo": "Congreso"},
    "20712": {"titulo": "Administración de Fondos", "organismo": "Congreso"},
    "18010": {"titulo": "Operaciones de Crédito de Dinero", "organismo": "Congreso"},
    "18045": {"titulo": "Mercado de Valores", "organismo": "Congreso"},
    "18046": {"titulo": "Sociedades Anónimas", "organismo": "Congreso"},
    "20345": {"titulo": "Sistemas de Pagos", "organismo": "Congreso"},
    "21000": {"titulo": "Comisión para el Mercado Financiero", "organismo": "Congreso"},
}

# DL 3500 se maneja aparte por ser decreto ley
DECRETOS_PRIORITARIOS = {
    "3500": {"titulo": "Sistema de Pensiones", "organismo": "Congreso", "tipo": "decreto_ley"},
}

BASE_URL = "https://www.bcn.cl/leychile"
API_URL = "https://www.bcn.cl/leychile/servicios/export"


class LeyChileScraper(BaseScraper):
    """Scraper para obtener leyes desde leychile.cl."""

    nombre = "leychile"

    async def obtener_normas(self, identificadores: list[str] | None = None) -> list[NormaRaw]:
        """Obtiene las normas desde leychile.cl."""
        if identificadores is None:
            identificadores = list(LEYES_PRIORITARIAS.keys()) + list(
                DECRETOS_PRIORITARIOS.keys()
            )

        normas = []
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            for numero in identificadores:
                try:
                    norma = await self._obtener_ley(client, numero)
                    if norma:
                        normas.append(norma)
                        self.logger.info("Obtenida: %s %s", norma.tipo, norma.numero)
                except Exception:
                    self.logger.exception("Error obteniendo ley %s", numero)

        self.logger.info("Total normas obtenidas: %d", len(normas))
        return normas

    async def _obtener_ley(self, client: httpx.AsyncClient, numero: str) -> NormaRaw | None:
        """Obtiene una ley específica por su número."""
        # Intentar obtener vía la página de consulta
        url = f"{BASE_URL}/navegar?idNorma=&idParte=&tipoNorma=0&buscar={numero}"
        response = await client.get(url)
        response.raise_for_status()

        # Intentar URL directa del texto vigente
        url_texto = f"{BASE_URL}/navegar?idNorma={self._buscar_id_norma(response.text, numero)}"
        if url_texto:
            response = await client.get(url_texto)
            response.raise_for_status()

        html = HTMLParser(response.text)
        return self._parsear_pagina(html, numero, response.url)

    def _buscar_id_norma(self, html_text: str, numero: str) -> str:
        """Busca el idNorma en la respuesta HTML de búsqueda."""
        # Buscar patrón idNorma=XXXXX en los links
        patron = re.compile(r"idNorma=(\d+)")
        matches = patron.findall(html_text)
        if matches:
            return matches[0]
        return ""

    def _parsear_pagina(self, html: HTMLParser, numero: str, url: str) -> NormaRaw | None:
        """Parsea la página HTML de una ley y extrae su contenido estructurado."""
        # Buscar el contenido principal de la norma
        contenido = html.css_first(".texto-norma, #texto_norma, .norma-body, #cuerpo")
        if not contenido:
            # Fallback: buscar en el body completo
            contenido = html.css_first("body")
            if not contenido:
                self.logger.warning("No se encontró contenido para ley %s", numero)
                return None

        texto_completo = contenido.text(strip=True)
        if not texto_completo or len(texto_completo) < 100:
            self.logger.warning("Contenido muy corto para ley %s (%d chars)", numero, len(texto_completo))
            return None

        # Determinar metadata
        info = LEYES_PRIORITARIAS.get(numero) or DECRETOS_PRIORITARIOS.get(numero, {})
        tipo = "decreto_ley" if numero in DECRETOS_PRIORITARIOS else "ley"

        # Extraer secciones estructurales
        secciones = self._extraer_secciones(contenido)

        # Extraer fecha de publicación si está disponible
        fecha_pub = self._extraer_fecha_publicacion(html)

        return NormaRaw(
            tipo=tipo,
            numero=numero,
            titulo=info.get("titulo", f"Ley {numero}"),
            organismo=info.get("organismo", "Congreso"),
            url_oficial=str(url),
            fecha_publicacion=fecha_pub,
            texto_completo=texto_completo,
            secciones=secciones,
        )

    def _extraer_secciones(self, nodo) -> list[dict]:
        """Extrae la estructura jerárquica: títulos, capítulos, artículos."""
        secciones = []
        articulo_actual = None
        texto_acumulado = []
        path_actual = []

        for elemento in nodo.iter():
            texto = elemento.text(strip=True) if elemento.text() else ""
            tag = elemento.tag

            if not texto:
                continue

            # Detectar títulos y capítulos
            if tag in ("h1", "h2", "h3", "h4") or self._es_encabezado(texto):
                # Guardar artículo anterior si existe
                if articulo_actual:
                    secciones.append({
                        "path": " > ".join(path_actual),
                        "numero": articulo_actual,
                        "texto": "\n".join(texto_acumulado),
                    })
                    texto_acumulado = []

                nivel = self._detectar_nivel(texto)
                if nivel == "titulo":
                    path_actual = [texto.strip()[:200]]
                elif nivel == "capitulo":
                    path_actual = path_actual[:1] + [texto.strip()[:200]]
                elif nivel == "parrafo":
                    path_actual = path_actual[:2] + [texto.strip()[:200]]

            # Detectar artículos
            match_art = re.match(
                r"^(Art[íi]culo|Art\.?)\s+(\d+[\w\s]*?)[\.\-\s]", texto, re.IGNORECASE
            )
            if match_art:
                # Guardar artículo anterior
                if articulo_actual:
                    secciones.append({
                        "path": " > ".join(path_actual),
                        "numero": articulo_actual,
                        "texto": "\n".join(texto_acumulado),
                    })

                articulo_actual = match_art.group(2).strip()
                texto_acumulado = [texto]
            elif articulo_actual:
                texto_acumulado.append(texto)

        # Guardar último artículo
        if articulo_actual and texto_acumulado:
            secciones.append({
                "path": " > ".join(path_actual),
                "numero": articulo_actual,
                "texto": "\n".join(texto_acumulado),
            })

        return secciones

    def _es_encabezado(self, texto: str) -> bool:
        """Detecta si un texto es un encabezado de sección."""
        patrones = [
            r"^T[ÍI]TULO\s+",
            r"^CAP[ÍI]TULO\s+",
            r"^P[ÁA]RRAFO\s+",
            r"^LIBRO\s+",
        ]
        return any(re.match(p, texto.upper().strip()) for p in patrones)

    def _detectar_nivel(self, texto: str) -> str:
        """Detecta el nivel jerárquico de un encabezado."""
        upper = texto.upper().strip()
        if re.match(r"^(LIBRO|T[ÍI]TULO)\s+", upper):
            return "titulo"
        if re.match(r"^CAP[ÍI]TULO\s+", upper):
            return "capitulo"
        if re.match(r"^P[ÁA]RRAFO\s+", upper):
            return "parrafo"
        return "otro"

    def _extraer_fecha_publicacion(self, html: HTMLParser) -> str | None:
        """Intenta extraer la fecha de publicación de la norma."""
        # Buscar en metadatos de la página
        for meta in html.css("meta"):
            name = meta.attributes.get("name", "")
            if "fecha" in name.lower() and "publicacion" in name.lower():
                return meta.attributes.get("content")

        # Buscar en el texto
        fecha_node = html.css_first(".fecha-publicacion, .fecha_publicacion")
        if fecha_node:
            return fecha_node.text(strip=True)

        return None

    async def verificar_cambios(self, hash_anterior: str, identificador: str) -> bool:
        """Verifica si una ley ha cambiado comparando hashes."""
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            norma = await self._obtener_ley(client, identificador)
            if norma:
                return norma.hash_contenido != hash_anterior
        return False
