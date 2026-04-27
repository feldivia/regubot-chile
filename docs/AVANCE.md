# Avance del proyecto ReguBot Chile

Ultima actualizacion: 2026-04-27

---

## Estado general: DEMO FUNCIONAL

La app esta deployada en Railway y la base de datos esta poblada con datos de semilla (5 leyes, 17 articulos). El chat funciona end-to-end con streaming SSE, RAG y Claude Haiku 4.5.

**URL produccion:** https://regubot-chile-production.up.railway.app/

---

## Completado

### Infraestructura
- [x] Monorepo (backend/ + frontend/) con Dockerfile raiz
- [x] Deploy en Railway (servicio unico backend+frontend)
- [x] PostgreSQL en Railway (servicio pgvector)
- [x] Variables de entorno configuradas (ANTHROPIC_API_KEY, OPENAI_API_KEY, DATABASE_URL)
- [x] Health check funcional (`/health`)
- [x] railway.toml en raiz con builder DOCKERFILE

### Backend (FastAPI)
- [x] Endpoint POST /api/chat con streaming SSE
- [x] Endpoint POST /api/chat/sync para testing
- [x] Endpoints admin (GET /api/stats, POST /api/reindex)
- [x] Config centralizada con pydantic-settings
- [x] Conexion async a PostgreSQL (asyncpg + SQLAlchemy)
- [x] Embeddings con OpenAI text-embedding-3-large (3072 dims)
- [x] LLM: Claude Haiku 4.5
- [x] Embeddings almacenados como JSONB (sin pgvector)

### Pipeline RAG
- [x] Intent classifier (heuristicas por keywords)
- [x] Query planner
- [x] Retriever (similitud coseno en Python sobre JSONB)
- [x] Generator con Claude + tool use para datos en vivo
- [x] Verificador anti-alucinacion (valida citas contra DB)
- [x] Formateador con tarjetas de trazabilidad

### Datos
- [x] Seed demo con 5 leyes y 17 articulos con embeddings
- [x] Script seed_demo.py (ingesta sin scraping)
- [x] Tablas: norma, articulo, chunk, query_log, relacion_norma

### Frontend (Next.js 14)
- [x] Chat UI con streaming SSE
- [x] Markdown rendering (react-markdown + remark-gfm)
- [x] Limpieza de [CITA:uuid] en tiempo real
- [x] CitationCard (tarjetas de fuentes)
- [x] LiveDataBadge (UF, TMC, etc.)
- [x] Disclaimer legal
- [x] Landing con sugerencias relevantes
- [x] Proxy API route (frontend -> backend server-side)
- [x] Build exitoso con `next build`

### Seguridad
- [x] Rate limiting por IP (3 consultas/dia, tabla PostgreSQL)
- [x] Deteccion de prompt injection (regex ES/EN)
- [x] Validacion de input (max 30 palabras, min 3 chars)
- [x] Admin endpoints protegidos con Bearer token (ADMIN_TOKEN)
- [x] CORS restringido a dominio especifico de produccion
- [x] Errores internos sanitizados (no exponen stack traces)
- [x] `.claude/` en .gitignore (prevenir leak de credenciales locales)

### Errores resueltos
- [x] 12 errores documentados en docs/ERRORES.md (ERR-001 a ERR-012)

---

## Pendiente

### Corto plazo (mejorar demo)
- [ ] Verificar que el chat responde correctamente con los datos de semilla
- [ ] Ajustar prompts si las respuestas no son buenas
- [ ] Probar datos en vivo (UF, TMC) — requiere credenciales BCCh o scraping CMF
- [ ] Agregar mas articulos al seed si es necesario

### Mediano plazo
- [ ] Resolver scraping de leychile.cl (Playwright o fuente alternativa)
- [ ] Agregar las 4 leyes faltantes (18.046, 20.712, 21.000, DL 3.500)
- [ ] Scrapers CMF, SII para normativa secundaria
- [ ] Alembic para migraciones de DB
- [ ] Tests automatizados (pytest)
- [ ] Evaluacion con golden_qa.jsonl

### Largo plazo
- [ ] Redis para cache
- [ ] CI/CD
- [ ] Registrarse en API Banco Central para datos en vivo completos
- [ ] Observabilidad (Sentry, logs estructurados)

---

## Decisiones tomadas

| Fecha | Decision | Razon |
|-------|----------|-------|
| 2026-04-26 | OpenAI embeddings | Pedido por el usuario |
| 2026-04-26 | Claude Haiku 4.5 | Modelo economico |
| 2026-04-26 | JSONB en vez de pgvector | PostgreSQL Railway no tiene pgvector |
| 2026-04-26 | Servicio unico | Un contenedor con start.sh, mas simple |
| 2026-04-26 | BCCh API opcional | Sin credenciales, no bloquea |
| 2026-04-26 | Redis opcional | Reduce costos Railway |
| 2026-04-27 | Seed demo hardcodeado | BCN migro a SPA Angular, scraper no funciona |
| 2026-04-27 | Rename RegBot -> ReguBot | Pedido por el usuario |

---

## Archivos eliminados (limpieza)

| Archivo | Razon |
|---------|-------|
| backend/Dockerfile | Deploy usa Dockerfile raiz |
| backend/railway.toml | Railway lee el de la raiz |
| frontend/Dockerfile | Frontend se build en Dockerfile raiz |
| frontend/railway.toml | No se usa |
| backend/nixpacks.toml | Railway usa Dockerfile, no Nixpacks |
| backend/Procfile | Railway usa Dockerfile |
| backend/scripts/bootstrap_corpus.py | Scraper BCN no funciona, reemplazado por seed_demo.py |
| backend/scripts/eval_qa.py | Dependia de golden_qa.jsonl eliminado |
| backend/jobs/ | Scheduler, refresh, reindex — dependen de APIs no configuradas |
| data/golden_qa.jsonl | Preguntas sobre datos no disponibles |
| docs/DEPLOY_RAILWAY.md | Info movida al README |
| docs/SOURCES.md | Info real esta en DATOS_DISPONIBLES.md |
| frontend/components/CitationCard.tsx | Reemplazado por CitasPanel con acordeon |
