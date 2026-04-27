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

**Solución final:** Eliminar dependencia de pgvector completamente. Almacenar embeddings como JSONB y calcular similitud coseno en Python. Esto funciona con cualquier PostgreSQL sin extensiones.

**Cambios:**
- `backend/app/models/chunk.py` — embedding cambiado de `Vector(3072)` a `JSONB`
- `backend/app/orchestrator/retriever.py` — similitud coseno calculada en Python en vez de operador pgvector
- `backend/app/main.py` — eliminado `CREATE EXTENSION vector`
- `backend/requirements.txt` y `pyproject.toml` — eliminada dependencia `pgvector`

**Lección:** No asumir que servicios "pgvector" de Railway realmente tienen la extensión. Usar JSONB es más portable y funciona en cualquier PostgreSQL.

---

## ERR-004: Dockerfile COPY no soporta sintaxis shell

**Fecha:** 2026-04-26
**Contexto:** Build del Dockerfile raiz y de frontend/Dockerfile en Railway.
**Error:**
```
COPY --from=frontend-builder /app/public ./public 2>/dev/null || true
```
El build falla porque Docker COPY no es un comando shell: no entiende `2>/dev/null` ni `|| true`. Interpreta esos tokens como paths adicionales a copiar, que no existen.

**Causa raiz:** Se intento usar una tecnica de "ignorar error" comun en shell (`|| true`), pero COPY es una instruccion nativa de Docker que no pasa por shell. Solo RUN ejecuta en shell.

**Solucion:** Crear el directorio `frontend/public/` con un `.gitkeep` para que siempre exista, y usar COPY directo sin trucos shell.

**Archivos afectados:** `Dockerfile`, `frontend/Dockerfile`, `backend/Dockerfile`

---

## ERR-005: CMD en exec form no expande variables de entorno

**Fecha:** 2026-04-26
**Contexto:** `backend/Dockerfile`
**Error:**
```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]
```
Uvicorn recibe literalmente la string `${PORT:-8000}` como numero de puerto, no el valor de la variable.

**Causa raiz:** En Docker, la exec form (JSON array) no pasa por shell, asi que las variables `${VAR}` no se expanden. Solo la shell form (`CMD comando args`) las expande.

**Solucion:** Cambiar a shell form: `CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`

**Archivo:** `backend/Dockerfile`

---

## ERR-006: Frontend sin package-lock.json

**Fecha:** 2026-04-26
**Contexto:** Build del frontend en Docker.
**Error:**
```
npm ci
npm ERR! The `npm ci` command can only install with an existing package-lock.json
```

**Causa raiz:** El frontend se creo sin ejecutar `npm install` localmente, por lo que nunca se genero `package-lock.json`. `npm ci` (usado en Docker para builds reproducibles) lo requiere obligatoriamente.

**Solucion:** Ejecutar `npm install` en `frontend/` para generar `package-lock.json` y commitearlo al repo.

**Archivo:** `frontend/package-lock.json`

---

## ERR-007: Error TypeScript en LiveDataBadge - tipo DatoVivo no asignable

**Fecha:** 2026-04-26
**Contexto:** Build del frontend con `next build`.
**Error:**
```
Type error: Type 'DatoVivo' is not assignable to type '{ [key: string]: unknown; ... }'.
Index signature for type 'string' is missing in type 'DatoVivo'.
```

**Causa raiz:** El componente LiveDataBadge definia su prop `dato` con un tipo inline con index signature `[key: string]: unknown`, pero el componente padre le pasaba un `DatoVivo` (interfaz sin index signature). TypeScript strict no permite esa asignacion.

**Solucion:** Cambiar la prop de LiveDataBadge para usar directamente el tipo `DatoVivo` importado de `@/lib/api`.

**Archivos:** `frontend/components/LiveDataBadge.tsx`, `frontend/components/Chat.tsx`

---

## ERR-008: No existia railway.toml en la raiz del repo

**Fecha:** 2026-04-26
**Contexto:** Deploy en Railway como servicio unico.
**Error:** Railway no sabia que builder usar. Railpack intentaba auto-detectar Python/Node pero fallaba por la estructura monorepo.

**Causa raiz:** Solo existian `backend/railway.toml` y `frontend/railway.toml`, pero ningun `railway.toml` en la raiz. Railway lee la config desde la raiz del repo (o Root Directory si esta configurado).

**Solucion:** Crear `railway.toml` en la raiz con `builder = "DOCKERFILE"` apuntando al Dockerfile raiz.

**Archivo:** `railway.toml`

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
