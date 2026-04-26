# Decisiones de diseño

## 2026-04-26: Clasificador de intención basado en heurísticas

**Decisión:** Usar un clasificador de intención basado en keywords en vez de un LLM separado.

**Razón:** Para V1, las heurísticas son suficientes y evitan una llamada extra a la API de Claude por cada consulta. Si la precisión no es suficiente, migrar a clasificación con LLM en V2.

## 2026-04-26: Chunking estructural vs. por tokens

**Decisión:** Respetar límites de artículos en el chunking. Un artículo corto = un chunk. Un artículo largo se divide por párrafos con overlap.

**Razón:** En normativa legal, la unidad semántica es el artículo. Cortar un artículo a la mitad produce chunks que pierden contexto regulatorio.

## 2026-04-26: Reciprocal Rank Fusion para búsqueda híbrida

**Decisión:** Usar RRF simple para fusionar resultados vectoriales y keyword.

**Razón:** Es simple, efectivo y no requiere entrenamiento. Reranker dedicado (ej. Cohere Rerank) queda para V2 si la precisión no alcanza.

## 2026-04-26: Sueldo mínimo hardcodeado

**Decisión:** Hardcodear el sueldo mínimo en vez de scrapearlo.

**Razón:** Cambia una vez al año y no hay API oficial. Actualización manual es aceptable para V1.
