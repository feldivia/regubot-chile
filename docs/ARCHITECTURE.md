# Arquitectura de RegBot Chile

## Vision general

RegBot Chile es un chatbot RAG (Retrieval-Augmented Generation) especializado en regulacion financiera chilena.

## Capas

### Frontend (Next.js 14)
- Chat UI con streaming SSE
- Tarjetas de trazabilidad por cada cita
- Mobile-first, accesible (WCAG AA)

### API Gateway (FastAPI)
- Rate limit por IP (requiere Redis)
- Logging estructurado
- Endpoints: `/api/chat` (streaming), `/api/chat/sync`, `/api/admin/stats`, `/health`
- Proxy catch-all: todo lo que no sea `/api` o `/health` se redirige a Next.js

### Orquestador
1. **Intent classifier** - Clasifica si es normativa, dato vivo, mixto, fuera de alcance
2. **Query planner** - Decide que fuentes consultar
3. **Retriever** - Busqueda hibrida (vectorial coseno en Python + keyword) con RRF
4. **Generator** - Claude con tool use para datos en vivo
5. **Verifier** - Valida citas contra la DB
6. **Formatter** - Tarjetas de trazabilidad con links a fuentes oficiales

### Almacenamiento
- **PostgreSQL**: normas, articulos, chunks con embeddings en JSONB
- **Redis** (opcional): cache de datos en vivo, rate limiting

### Pipeline de ingesta
- Scrapers por fuente (leychile, CMF, SII, BCCh, SP, SERNAC)
- Parser que preserva jerarquia (Ley > Titulo > Capitulo > Articulo)
- Chunking estructural (nunca corta un articulo a la mitad)
- Deteccion de cambios por hash SHA256

## Flujo de una consulta

```
Usuario -> Intent -> Plan -> [RAG + Datos Vivos] -> Claude -> Verificacion -> Formato -> Respuesta
```

## Deploy

### Servicio unico (default)
Un solo contenedor Railway ejecuta backend (uvicorn) + frontend (Next.js standalone):
- `start.sh` levanta Next.js en background (puerto 3000) y uvicorn en foreground (puerto $PORT)
- FastAPI proxea requests GET/HEAD no-API a Next.js
- `Dockerfile` raiz construye ambos en multi-stage build
- `railway.toml` raiz con `builder = "DOCKERFILE"`

### Dos servicios (alternativa)
Backend y frontend como servicios Railway separados:
- Cada uno tiene su propio `Dockerfile` y `railway.toml`
- Frontend se comunica con backend via `BACKEND_INTERNAL_URL` (red interna Railway)
- Configurar Root Directory en Railway: `backend/` y `frontend/` respectivamente
