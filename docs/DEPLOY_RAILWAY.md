# Guia de deploy en Railway

## Prerequisitos

- Cuenta en [railway.app](https://railway.app)
- Repositorio del proyecto conectado a GitHub
- API keys de Anthropic y OpenAI

---

## Paso 1: Crear proyecto en Railway

1. Ir a [railway.app/new](https://railway.app/new)
2. Click "Deploy from GitHub repo"
3. Seleccionar el repositorio del proyecto

---

## Paso 2: Agregar PostgreSQL con pgvector

**IMPORTANTE:** Se necesita PostgreSQL con la extensión pgvector. El PostgreSQL nativo de Railway NO incluye pgvector.

### Opcion A: Template pgvector en Railway (recomendado)
1. Click **"New"** > **"Template"**
2. Buscar **"pgvector"** y desplegar el template
3. Railway crea la DB con pgvector preinstalado y genera `DATABASE_URL`

### Opcion B: Proveedor externo con pgvector
Si no hay template disponible, usar un proveedor externo gratuito:
- **Neon** (neon.tech) — PostgreSQL serverless con pgvector incluido, tier gratuito
- **Supabase** (supabase.com) — PostgreSQL con pgvector, tier gratuito

Configurar `DATABASE_URL` manualmente en las variables del backend con la connection string del proveedor.

### Verificar pgvector
La app ejecuta `CREATE EXTENSION IF NOT EXISTS vector` automaticamente al arrancar. Si falla, el backend mostrara un error claro en los logs.

---

## Paso 3: Configurar variables de entorno del backend

En el servicio del backend, ir a **Variables** y agregar:

### Obligatorias

| Variable | Valor | Descripcion |
|----------|-------|-------------|
| `ANTHROPIC_API_KEY` | `sk-ant-...` | API key de Anthropic para Claude |
| `OPENAI_API_KEY` | `sk-...` | API key de OpenAI para embeddings |
| `DATABASE_URL` | (auto) | Railway la inyecta automaticamente al vincular PostgreSQL |

### Opcionales

| Variable | Valor por defecto | Descripcion |
|----------|-------------------|-------------|
| `REDIS_URL` | (vacio) | URL de Redis. Sin ella, cache y rate limiting se desactivan |
| `BCCH_USER` | (vacio) | Usuario API Banco Central. Sin el, UF/UTM/TPM/dolar/IPC no disponibles |
| `BCCH_PASSWORD` | (vacio) | Password API Banco Central |
| `CLAUDE_MODEL` | `claude-haiku-4-5-20251001` | Modelo de Claude a usar |
| `EMBEDDING_MODEL` | `text-embedding-3-large` | Modelo de embeddings OpenAI |
| `EMBEDDING_DIMENSIONS` | `3072` | Dimensiones del vector |
| `LOG_LEVEL` | `INFO` | Nivel de logging (DEBUG, INFO, WARNING, ERROR) |
| `RATE_LIMIT_PER_MIN` | `20` | Maximo de requests por IP por minuto (requiere Redis) |
| `SENTRY_DSN` | (vacio) | DSN de Sentry para monitoreo de errores |

---

## Paso 4: Vincular PostgreSQL al backend

1. Click en el servicio del backend
2. Ir a **Variables** > **Reference Variables**
3. Vincular `DATABASE_URL` desde el servicio PostgreSQL
4. Railway inyecta la URL automaticamente

**Nota:** Railway provee `DATABASE_URL` con prefijo `postgresql://`. La app lo convierte automaticamente a `postgresql+asyncpg://` (ver `backend/app/db/session.py`).

---

## Paso 5: Deploy del frontend

### Opcion A: Servicio separado en Railway

1. Click **"New"** > **"GitHub Repo"** > seleccionar el mismo repo
2. En **Settings** > **Source** > **Root Directory**: escribir `frontend`
3. Configurar variables:

| Variable | Valor | Descripcion |
|----------|-------|-------------|
| `NEXT_PUBLIC_API_URL` | URL publica del backend (ej: `https://<nombre-servicio>.up.railway.app`) | URL publica del backend |
| `BACKEND_INTERNAL_URL` | URL interna del backend (ej: `http://<nombre-servicio>.railway.internal:8000`) | URL interna entre servicios (mas rapida, gratis) |

### Opcion B: Frontend en Vercel (alternativa)

1. Importar repo en [vercel.com](https://vercel.com)
2. Root Directory: `frontend`
3. Variable: `NEXT_PUBLIC_API_URL` = URL del backend en Railway

---

## Paso 6: (Opcional) Agregar Redis

1. Click **"New"** > **"Database"** > **"Redis"**
2. Vincular `REDIS_URL` al servicio del backend
3. Con Redis habilitado se activan: cache de datos en vivo y rate limiting por IP

---

## Paso 7: Verificar deploy

### Backend
- Abrir `https://<url-del-backend>/health`
- Debe retornar: `{"status": "ok", "database": "connected"}`

### Estadisticas
- `https://<url-del-backend>/api/admin/stats`
- Muestra conteo de normas, articulos, chunks y consultas

### Frontend
- Abrir la URL del frontend
- Escribir una pregunta de prueba

---

## Paso 8: Ingestar corpus inicial

Despues del primer deploy exitoso, ejecutar la ingesta de las leyes prioritarias.
Opciones:

### Desde Railway (recomendado)
- Ir al backend > **Settings** > **Cron Jobs** o ejecutar via API:
```bash
curl -X POST https://<url-del-backend>/api/admin/reindex
```

### Desde local contra la DB de Railway
```bash
# Copiar DATABASE_URL de Railway
export DATABASE_URL="postgresql://..."
export OPENAI_API_KEY="sk-..."
cd backend
pip install -r requirements.txt
python scripts/bootstrap_corpus.py
```

---

## Troubleshooting

### "No start command detected"
El Dockerfile debe estar en la RAIZ del repo, no en `backend/`. Ver `docs/ERRORES.md` ERR-001.

### Backend arranca pero DB no conecta
Verificar que `DATABASE_URL` esta vinculada correctamente en Variables. Railway debe mostrarla como referencia al servicio PostgreSQL.

### pgvector no funciona
Ejecutar `CREATE EXTENSION IF NOT EXISTS vector;` en la DB. Sin esto, los embeddings no se pueden almacenar.

### Frontend no conecta con backend
- Verificar que `NEXT_PUBLIC_API_URL` apunta a la URL publica del backend (con `https://`)
- Verificar que el backend tiene CORS configurado para `*.railway.app`
- Para comunicacion interna, usar `BACKEND_INTERNAL_URL` con la URL `*.railway.internal`
