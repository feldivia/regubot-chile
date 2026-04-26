"""Tests para el parser normativo."""

import pytest

from app.ingestion.base import NormaRaw
from app.ingestion.parser import parsear_norma


def _crear_norma_raw(texto: str, secciones: list | None = None) -> NormaRaw:
    return NormaRaw(
        tipo="ley",
        numero="19496",
        titulo="Protección del Consumidor",
        organismo="Congreso",
        url_oficial="https://www.bcn.cl/leychile/navegar?idNorma=61438",
        texto_completo=texto,
        secciones=secciones or [],
    )


class TestParser:
    def test_parsea_articulos_simples(self):
        texto = """
        TITULO I
        DISPOSICIONES GENERALES

        Artículo 1.- Esta ley regula las relaciones entre proveedores y consumidores.

        Artículo 2.- Solo quedan sujetos a las disposiciones de esta ley los actos
        jurídicos que tengan el carácter de mercantiles.

        Artículo 3.- Son derechos y deberes básicos del consumidor:
        a) La libre elección del bien o servicio.
        b) El derecho a una información veraz y oportuna.
        """
        raw = _crear_norma_raw(texto)
        parsed = parsear_norma(raw)

        assert parsed.tipo == "ley"
        assert parsed.numero == "19496"
        assert len(parsed.articulos) == 3
        assert parsed.articulos[0].numero == "1"
        assert parsed.articulos[1].numero == "2"
        assert parsed.articulos[2].numero == "3"

    def test_parsea_desde_secciones(self):
        secciones = [
            {
                "path": "Titulo I > Art 1",
                "numero": "1",
                "texto": "Esta ley regula las relaciones entre proveedores y consumidores.",
            },
            {
                "path": "Titulo I > Art 2",
                "numero": "2",
                "texto": "Solo quedan sujetos a esta ley los actos mercantiles.",
            },
        ]
        raw = _crear_norma_raw("texto completo", secciones)
        parsed = parsear_norma(raw)

        assert len(parsed.articulos) == 2
        assert parsed.articulos[0].path == "Titulo I > Art 1"

    def test_norma_sin_articulos_usa_texto_completo(self):
        texto = "Este es un texto normativo sin artículos identificables pero con contenido."
        raw = _crear_norma_raw(texto)
        parsed = parsear_norma(raw)

        assert len(parsed.articulos) == 1
        assert parsed.articulos[0].numero == "completo"

    def test_hash_contenido_se_preserva(self):
        raw = _crear_norma_raw("Texto de prueba")
        parsed = parsear_norma(raw)
        assert parsed.hash_contenido == raw.hash_contenido

    def test_parsea_articulos_con_bis(self):
        texto = """
        Artículo 17.- Texto del artículo 17.

        Artículo 17 bis.- Texto del artículo 17 bis agregado después.

        Artículo 18.- Texto del artículo 18.
        """
        raw = _crear_norma_raw(texto)
        parsed = parsear_norma(raw)

        assert len(parsed.articulos) >= 2
