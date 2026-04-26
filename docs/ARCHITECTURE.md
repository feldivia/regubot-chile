# Arquitectura de RegBot Chile

## Visión general

RegBot Chile es un chatbot RAG (Retrieval-Augmented Generation) especializado en regulación financiera chilena.

## Capas

### Frontend (Next.js 14)
- Chat UI con streaming SSE
- Tarjetas de trazabilidad por cada cita
- Mobile-first, accesible (WCAG AA)

### API Gateway (FastAPI)
- Rate limit por IP
- Logging estructurado
- Endpoints: `/api/chat` (streaming), `/api/chat/sync`, `/api/admin/stats`, `/health`

### Orquestador
1. **Intent classifier** - Clasifica si es normativa, dato vivo, mixto, fuera de alcance
2. **Query planner** - Decide qué fuentes consultar
3. **Retriever** - Búsqueda híbrida (vectorial + keyword) en pgvector
4. **Generator** - Claude con tool use para datos en vivo
5. **Verifier** - Valida citas contra la DB
6. **Formatter** - Tarjetas de trazabilidad con links a fuentes oficiales

### Almacenamiento
- **PostgreSQL + pgvector**: normas, artículos, chunks vectorizados
- **Redis**: cache de datos en vivo, rate limiting

### Pipeline de ingesta
- Scrapers por fuente (leychile, CMF, SII, BCCh, SP, SERNAC)
- Parser que preserva jerarquía (Ley > Título > Capítulo > Artículo)
- Chunking estructural (nunca corta un artículo a la mitad)
- Detección de cambios por hash SHA256

## Flujo de una consulta

```
Usuario -> Intent -> Plan -> [RAG + Datos Vivos] -> Claude -> Verificación -> Formato -> Respuesta
```
