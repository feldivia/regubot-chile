# Registro de errores y soluciones

Este archivo documenta errores encontrados durante el desarrollo y deploy.
Consultar SIEMPRE antes de hacer cambios en configuración de deploy o infraestructura.

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

**Causa raíz:** Railway migró de Nixpacks a Railpack (v0.23.0) como builder por defecto. Railpack ignora `nixpacks.toml`, `railpack.toml` y `Procfile` cuando no están en la raíz o no siguen el formato esperado. Además, al ser un monorepo, el código Python está en `backend/` y no en la raíz, por lo que Railpack no encuentra `requirements.txt` ni `app/main.py`.

**Intentos fallidos:**
1. `backend/Procfile` - Railway no lo lee porque despliega desde la raíz
2. `backend/nixpacks.toml` - Railpack ignora formato Nixpacks
3. `nixpacks.toml` en raíz - Railpack ignora formato Nixpacks
4. `railpack.toml` en raíz - Railpack no lo reconoció
5. `backend/railway.toml` con `builder = "DOCKERFILE"` - No se lee sin Root Directory configurado

**Solucion final:** Crear un `Dockerfile` en la raíz del repo que copia e instala desde `backend/`. Railway siempre detecta un Dockerfile en la raíz.

**Lección:** En monorepos con Railway, la opción más confiable es un `Dockerfile` en la raíz. Alternativa: configurar Root Directory en el dashboard de Railway, pero eso requiere intervención manual.

---

## ERR-002: DATABASE_URL incompatible con asyncpg

**Fecha:** 2026-04-26
**Contexto:** Conexión a PostgreSQL de Railway
**Error previsto:** Railway provee `DATABASE_URL` con prefijo `postgresql://`, pero SQLAlchemy async necesita `postgresql+asyncpg://`.

**Solución:** Se agregó `_build_db_url()` en `backend/app/db/session.py` que convierte automáticamente el prefijo.

**Archivo:** `backend/app/db/session.py`

---

## ERR-003: pgvector no disponible en PostgreSQL de Railway

**Fecha:** 2026-04-26
**Contexto:** Primer deploy del backend en Railway. PostgreSQL arranca bien pero la app crashea al crear tablas.
**Error:**
```
ERROR: type "vector" does not exist at character 106
CREATE TABLE chunk (... embedding VECTOR(3072) ...)
```

**Causa raíz:** La imagen de PostgreSQL nativa de Railway (PostgreSQL 17.9 Debian) no incluye la extensión pgvector preinstalada. `CREATE EXTENSION IF NOT EXISTS vector` falla porque el paquete no existe en el sistema, no solo porque no está habilitada.

**Solución:** En Railway, usar el template **"PostgreSQL + pgvector"** en vez del PostgreSQL nativo:
1. Eliminar el servicio PostgreSQL actual
2. Click **"New"** > buscar **"pgvector"** en los templates
3. Desplegar el template de pgvector
4. Re-vincular `DATABASE_URL` al backend

**Alternativa:** Si no hay template de pgvector disponible, se puede usar Neon (neon.tech) o Supabase como proveedor externo de PostgreSQL con pgvector, y configurar `DATABASE_URL` manualmente.

**Archivo:** `backend/app/main.py` (mejorado manejo de error para loguear instrucciones claras)

---

## Plantilla para nuevos errores

```
## ERR-XXX: [Título descriptivo]

**Fecha:** YYYY-MM-DD
**Contexto:** [Dónde ocurrió]
**Error:** [Mensaje de error]
**Causa raíz:** [Por qué ocurrió]
**Solución:** [Qué se hizo]
**Archivo(s) afectado(s):** [Qué se modificó]
```
