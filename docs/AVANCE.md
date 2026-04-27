# Avance del proyecto RegBot Chile

Ultima actualizacion: 2026-04-26

---

## Estado general: EN PROGRESO - Fase 0/1 (Setup + Deploy)

---

## Completado

### Fase 0 - Setup
- [x] Estructura monorepo (backend/ + frontend/)
- [x] docker-compose.yml para dev local (PostgreSQL, Redis)
- [x] .env.example con todas las variables
- [x] pyproject.toml y requirements.txt
- [x] .gitignore
- [x] Dockerfile raiz para deploy Railway (servicio unico backend+frontend)
- [x] Dockerfiles individuales (backend, frontend) para deploy en 2 servicios
- [x] railway.toml en raiz + por servicio
- [x] Repo en GitHub: github.com/feldivia/regubot-chile
- [x] Frontend: package-lock.json, public/, next-env.d.ts

### Fase 1 - Ingesta (codigo creado, sin probar)
- [x] Clase base Scraper abstracta
- [x] Scraper leychile.cl (9 leyes prioritarias)
- [x] Scrapers CMF, SII, BCCh, SP, SERNAC
- [x] Parser normativo (jerarquia Titulo > Capitulo > Articulo)
- [x] Chunker estructural (no corta articulos a la mitad)
- [x] Pipeline de ingesta idempotente (deteccion cambios por hash)
- [x] Script bootstrap_corpus.py

### Fase 2 - Orquestador RAG + Claude (codigo creado, sin probar)
- [x] Intent classifier (heuristicas por keywords)
- [x] Query planner
- [x] Retriever hibrido (vectorial JSONB + keyword con RRF)
- [x] Generator con Claude Haiku 4.5 + tool use
- [x] Verificador anti-alucinacion
- [x] Formateador con tarjetas de trazabilidad
- [x] Endpoint POST /chat con streaming SSE
- [x] Endpoint POST /chat/sync para testing
- [x] Endpoints admin (stats, reindex)
- [x] Health check

### Fase 3 - Datos en vivo (codigo creado, sin probar)
- [x] Cliente API Banco Central (UF, UTM, TPM, dolar, IPC) - requiere credenciales BCCh
- [x] Scraper CMF para TMC
- [x] Sueldo minimo hardcodeado
- [x] Cache Redis opcional
- [x] Tools expuestos a Claude via tool use
- [x] Jobs programados (refresh horario, reindex diario)

### Frontend (codigo creado, compila correctamente)
- [x] Next.js 14 App Router + TypeScript + Tailwind
- [x] Chat UI con streaming SSE
- [x] Componente Message con avatar
- [x] CitationCard (tarjetas de trazabilidad)
- [x] LiveDataBadge (UF, TMC, etc.)
- [x] Disclaimer persistente
- [x] Landing con sugerencias
- [x] Proxy API route
- [x] Build exitoso con `next build`

### Prompts y documentacion
- [x] system.md, intent.md, verifier.md, formatter.md
- [x] ARCHITECTURE.md, SOURCES.md, LEGAL.md, DECISIONS.md
- [x] golden_qa.jsonl (15 casos de evaluacion)
- [x] Script eval_qa.py

### Configuracion
- [x] Embeddings: OpenAI text-embedding-3-large (3072 dims)
- [x] LLM: Claude Haiku 4.5 (economico)
- [x] BCCh API: opcional (no bloquea si no hay credenciales)
- [x] Redis: opcional (funciona sin el)
- [x] Embeddings almacenados como JSONB (no requiere pgvector)

### Errores de deploy resueltos
- [x] ERR-001: Railway Railpack no detecta start command -> Dockerfile en raiz
- [x] ERR-002: DATABASE_URL incompatible con asyncpg -> conversion automatica en session.py
- [x] ERR-003: pgvector no disponible -> eliminado, usando JSONB
- [x] ERR-004: Docker COPY con sintaxis shell -> COPY directo, public/ creado
- [x] ERR-005: CMD exec form no expande variables -> shell form
- [x] ERR-006: Faltaba package-lock.json -> generado
- [x] ERR-007: TypeScript error en LiveDataBadge -> tipos alineados
- [x] ERR-008: Sin railway.toml en raiz -> creado

---

## Pendiente

### Deploy Railway
- [x] Dockerfile en raiz del repo (corregido, funcional)
- [x] railway.toml en raiz con builder DOCKERFILE
- [ ] Primer deploy exitoso (push hecho, pendiente verificar en Railway)
- [ ] Configurar variables de entorno en Railway (ANTHROPIC_API_KEY, OPENAI_API_KEY, DATABASE_URL)
- [ ] Verificar health check funciona (`/health`)

### Validacion funcional
- [ ] Probar ingesta de al menos 3 leyes con bootstrap_corpus.py
- [ ] Verificar que scraper de leychile.cl extrae articulos correctamente (selectores CSS pueden necesitar ajuste)
- [ ] Probar endpoint /chat con pregunta real
- [ ] Verificar streaming SSE funciona end-to-end
- [ ] Probar verificacion de citas
- [ ] Probar datos en vivo (TMC al menos, no requiere BCCh)

### Testing
- [ ] Correr pytest y verificar que tests pasan
- [ ] Ajustar tests si hay imports rotos
- [ ] Evaluar con golden_qa.jsonl

### Pendiente futuro (no esta etapa)
- [ ] Registrarse en API Banco Central (BCCH_USER/BCCH_PASSWORD) para datos en vivo completos
- [ ] Agregar Redis en Railway para cache
- [ ] Scrapers Tier 2 (SII, SP, SERNAC) - probados en sitios reales
- [ ] Tuning de retrieval (top_k, similarity_threshold)
- [ ] Alembic para migraciones de DB
- [ ] CI/CD (lint, tests automaticos)
- [ ] Rate limiting real (requiere Redis)
- [ ] Observabilidad (Sentry, logs estructurados)

---

## Decisiones tomadas

| Fecha | Decision | Razon |
|-------|----------|-------|
| 2026-04-26 | OpenAI embeddings en vez de Voyage AI | Pedido por el usuario |
| 2026-04-26 | Claude Haiku 4.5 en vez de Opus | Modelo mas economico |
| 2026-04-26 | BCCh API opcional | Dejado fuera de esta etapa |
| 2026-04-26 | Redis opcional | Funciona sin el, reduce costos Railway |
| 2026-04-26 | Dockerfile en raiz | Railway Railpack no detectaba start command en monorepo |
| 2026-04-26 | JSONB en vez de pgvector | PostgreSQL de Railway no tiene pgvector; JSONB es portable |
| 2026-04-26 | Servicio unico (backend+frontend) | Mas simple para Railway, un solo contenedor con start.sh |
