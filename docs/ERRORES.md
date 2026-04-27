# Registro de errores y soluciones

Este archivo documenta errores encontrados durante el desarrollo y deploy.
Consultar SIEMPRE antes de hacer cambios en configuracion de deploy o infraestructura.

---

## ERR-001: Railway no detecta start command con Railpack

**Fecha:** 2026-04-26
**Contexto:** Deploy del backend en Railway
**Error:**
```
using build driver railpack-v0.23.0
Detected Python
No start command detected. Specify a start command
```

**Causa raiz:** Railway migro de Nixpacks a Railpack como builder. Railpack ignora `nixpacks.toml`, `railpack.toml` y `Procfile`. Al ser monorepo, no encuentra `requirements.txt` ni `app/main.py` en la raiz.

**Intentos fallidos:**
1. `backend/Procfile` - Railway no lo lee
2. `nixpacks.toml` en raiz - Railpack ignora formato Nixpacks
3. `railpack.toml` en raiz - Railpack no lo reconocio

**Solucion:** Crear un `Dockerfile` en la raiz del repo. Railway siempre detecta un Dockerfile en la raiz.

---

## ERR-002: DATABASE_URL incompatible con asyncpg

**Fecha:** 2026-04-26
**Contexto:** Conexion a PostgreSQL de Railway
**Error:** Railway provee `DATABASE_URL` con prefijo `postgresql://`, pero SQLAlchemy async necesita `postgresql+asyncpg://`.

**Solucion:** `_build_db_url()` en `backend/app/db/session.py` convierte automaticamente el prefijo.

---

## ERR-003: pgvector no disponible en PostgreSQL de Railway

**Fecha:** 2026-04-26
**Contexto:** Primer deploy, PostgreSQL crashea al crear tablas.
**Error:** `ERROR: type "vector" does not exist`

**Causa raiz:** PostgreSQL nativo de Railway no incluye pgvector.

**Solucion:** Eliminar pgvector. Embeddings como JSONB, similitud coseno en Python.

---

## ERR-004: Dockerfile COPY no soporta sintaxis shell

**Fecha:** 2026-04-26
**Error:** `COPY --from=frontend-builder /app/public ./public 2>/dev/null || true` falla.

**Causa raiz:** COPY es instruccion Docker nativa, no shell. No entiende `2>/dev/null` ni `|| true`.

**Solucion:** Crear `frontend/public/` con `.gitkeep` y usar COPY directo.

---

## ERR-005: CMD en exec form no expande variables de entorno

**Fecha:** 2026-04-26
**Error:** Uvicorn recibe literalmente `${PORT:-8000}` como string.

**Causa raiz:** Docker exec form (JSON array) no pasa por shell.

**Solucion:** Cambiar a shell form: `CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`

---

## ERR-006: Frontend sin package-lock.json

**Fecha:** 2026-04-26
**Error:** `npm ci` requiere `package-lock.json`.

**Solucion:** Ejecutar `npm install` para generar `package-lock.json` y commitearlo.

---

## ERR-007: Error TypeScript en LiveDataBadge

**Fecha:** 2026-04-26
**Error:** `Type 'DatoVivo' is not assignable to type '{ [key: string]: unknown; ... }'`

**Solucion:** Cambiar prop de LiveDataBadge para usar tipo `DatoVivo` directamente.

---

## ERR-008: Sin railway.toml en la raiz del repo

**Fecha:** 2026-04-26
**Solucion:** Crear `railway.toml` en la raiz con `builder = "DOCKERFILE"`.

---

## ERR-009: Frontend llamando a localhost:8000 en produccion

**Fecha:** 2026-04-26
**Contexto:** App deployada en Railway, usuario abre el chat.
**Error:** `POST http://localhost:8000/api/chat net::ERR_CONNECTION_REFUSED`

**Causa raiz:** `Chat.tsx` tenia `const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'`. En produccion, `NEXT_PUBLIC_API_URL` no estaba definida, asi que el browser del usuario intentaba conectar a su propio localhost.

**Solucion:** Cambiar fallback a `''` (string vacia). Asi `fetch('/api/chat')` va al proxy de Next.js (`app/api/chat/route.ts`), que reenvía al backend server-side.

**Leccion:** Variables `NEXT_PUBLIC_*` se inyectan en build time. Si no estan definidas en el build, el fallback es lo que queda en el JS del browser.

---

## ERR-010: Pydantic rechaza variables extra del .env

**Fecha:** 2026-04-26
**Contexto:** Ejecutar `seed_demo.py` localmente.
**Error:** `Extra inputs are not permitted [type=extra_forbidden, input_value='http://localhost:8000']` para `NEXT_PUBLIC_API_URL`.

**Causa raiz:** Pydantic Settings por defecto usa `extra = "forbid"`. El `.env` incluye variables del frontend que el backend no reconoce.

**Solucion:** Agregar `"extra": "ignore"` en `model_config` de `Settings`.

---

## ERR-011: Columna embedding tipo vector (viejo) vs JSONB (nuevo)

**Fecha:** 2026-04-26
**Contexto:** Ejecutar seed_demo contra la DB de Railway.
**Error:** `column "embedding" is of type vector but expression is of type jsonb`

**Causa raiz:** Las tablas se habian creado en un deploy anterior con el schema viejo (pgvector). El codigo nuevo usa JSONB pero la tabla en la DB seguia con tipo `vector`.

**Solucion:** Dropear tablas y dejar que `Base.metadata.create_all` las recree con JSONB.

**Leccion:** Sin Alembic, los cambios de schema requieren drop+recreate manual. Considerar agregar migraciones para V2.

---

## ERR-012: Scraper de leychile.cl no obtiene contenido (SPA Angular)

**Fecha:** 2026-04-26
**Contexto:** Ejecutar `bootstrap_corpus.py` — scraper retorna 0 normas.
**Error:** `Contenido muy corto para ley 19496 (8 chars)` para las 9 leyes.

**Causa raiz:** BCN migro leychile.cl a una SPA Angular. Todas las URLs devuelven una shell HTML de 9KB sin contenido. El contenido se carga via JavaScript. No hay API publica accesible. La API XML devuelve error Oracle.

**Solucion:** Crear `seed_demo.py` con textos de articulos clave hardcodeados (5 leyes, 17 articulos). Suficiente para demo. Para produccion, considerar Playwright para renderizar la SPA o buscar fuentes alternativas.

---

## Plantilla para nuevos errores

```
## ERR-XXX: [Titulo descriptivo]

**Fecha:** YYYY-MM-DD
**Contexto:** [Donde ocurrio]
**Error:** [Mensaje de error]
**Causa raiz:** [Por que ocurrio]
**Solucion:** [Que se hizo]
**Archivo(s) afectado(s):** [Que se modifico]
```
