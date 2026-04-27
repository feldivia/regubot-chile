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

Railway detectara el `Dockerfile` en la raiz y usara `builder = "DOCKERFILE"` (configurado en `railway.toml`).

---

## Paso 2: Agregar PostgreSQL

Se usa PostgreSQL estandar (sin pgvector). Los embeddings se almacenan como JSONB y la similitud coseno se calcula en Python.

1. Click **"New"** > **"Database"** > **"PostgreSQL"**
2. Railway crea la DB y genera `DATABASE_URL` automaticamente

**Nota:** La app convierte automaticamente el prefijo `postgresql://` a `postgresql+asyncpg://` (ver `backend/app/db/session.py`).

---

## Paso 3: Configurar variables de entorno

En el servicio principal, ir a **Variables** y agregar:

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
| `LOG_LEVEL` | `INFO` | Nivel de logging |
| `SENTRY_DSN` | (vacio) | DSN de Sentry para monitoreo de errores |

---

## Paso 4: Vincular PostgreSQL

1. Click en el servicio principal
2. Ir a **Variables** > **Reference Variables**
3. Vincular `DATABASE_URL` desde el servicio PostgreSQL

---

## Paso 5: (Opcional) Agregar Redis

1. Click **"New"** > **"Database"** > **"Redis"**
2. Vincular `REDIS_URL` al servicio principal
3. Con Redis habilitado se activan: cache de datos en vivo y rate limiting por IP

---

## Paso 6: Verificar deploy

### Health check
- Abrir `https://<url-del-servicio>/health`
- Debe retornar: `{"status": "ok", "database": "connected"}`

### Frontend
- Abrir `https://<url-del-servicio>/`
- Debe mostrar la landing page de RegBot

### Estadisticas
- `https://<url-del-servicio>/api/admin/stats`

---

## Paso 7: Ingestar corpus inicial

Despues del primer deploy exitoso, ejecutar la ingesta:

### Desde local contra la DB de Railway
```bash
# Copiar DATABASE_URL de Railway
export DATABASE_URL="postgresql://..."
export OPENAI_API_KEY="sk-..."
cd backend
pip install -r requirements.txt
python scripts/bootstrap_corpus.py
```

### Via API
```bash
curl -X POST https://<url-del-servicio>/api/admin/reindex
```

---

## Troubleshooting

### "No start command detected"
El `railway.toml` en la raiz debe tener `builder = "DOCKERFILE"`. Ver `docs/ERRORES.md` ERR-001.

### Backend arranca pero DB no conecta
Verificar que `DATABASE_URL` esta vinculada correctamente en Variables.

### Frontend muestra "Frontend no disponible"
Next.js puede tardar unos segundos en levantar. El `start.sh` espera hasta 30s. Si persiste, revisar logs del contenedor.

### Build falla en COPY public
Asegurarse de que `frontend/public/` existe (debe tener al menos `.gitkeep`). Ver ERR-004.

### Build falla en npm ci
Asegurarse de que `frontend/package-lock.json` esta commiteado. Ver ERR-006.
