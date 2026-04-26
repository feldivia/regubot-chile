"""Tests para el chunker estructural."""

import pytest

from app.ingestion.chunker import MAX_CHUNK_CHARS, MIN_CHUNK_CHARS, chunkear_articulo
from app.ingestion.parser import ArticuloParsed


class TestChunker:
    def test_articulo_corto_no_se_divide(self):
        articulo = ArticuloParsed(
            numero="1",
            path="Titulo I > Art 1",
            texto="Esta ley regula las relaciones entre proveedores y consumidores.",
            orden=0,
        )
        chunks = chunkear_articulo(articulo, "Ley 19.496")

        assert len(chunks) == 1
        assert chunks[0]["metadata"]["articulo_numero"] == "1"
        assert chunks[0]["metadata"]["norma_titulo"] == "Ley 19.496"

    def test_articulo_largo_se_divide(self):
        # Crear texto largo que exceda MAX_CHUNK_CHARS
        texto_largo = "\n\n".join([f"Párrafo {i}: " + "X" * 400 for i in range(20)])
        articulo = ArticuloParsed(
            numero="50",
            path="Titulo V > Art 50",
            texto=texto_largo,
            orden=5,
        )
        chunks = chunkear_articulo(articulo, "Ley 18.010")

        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk["texto"]) <= MAX_CHUNK_CHARS + 500  # Margen por overlap

    def test_articulo_vacio_no_genera_chunks(self):
        articulo = ArticuloParsed(numero="0", path="", texto="", orden=0)
        chunks = chunkear_articulo(articulo, "Test")
        assert len(chunks) == 0

    def test_metadata_incluida(self):
        articulo = ArticuloParsed(
            numero="3",
            path="Titulo I > Capitulo 2 > Art 3",
            texto="Texto del artículo con información relevante para el consumidor.",
            orden=2,
        )
        chunks = chunkear_articulo(articulo, "Ley 19.496")

        assert chunks[0]["metadata"]["path"] == "Titulo I > Capitulo 2 > Art 3"
        assert chunks[0]["tokens"] > 0
