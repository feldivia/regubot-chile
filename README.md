# ReguBot Chile

Chatbot con IA que convierte la regulación financiera chilena en respuestas que cualquier persona puede entender, verificadas en tiempo real contra datos oficiales.

## Stack

- **Frontend:** Next.js 14 + TypeScript + Tailwind CSS
- **Backend:** FastAPI (Python 3.11+)
- **LLM:** Claude (Anthropic) con tool use
- **Vector store:** PostgreSQL + pgvector
- **Embeddings:** OpenAI (text-embedding-3-large)
- **Cache:** Redis (opcional)
- **Deploy:** Railway

## Inicio rápido

### 1. Clonar y configurar

```bash
cp .env.example .env
# Editar .env con tus API keys
```

### 2. Levantar servicios

```bash
docker compose up -d
```

### 3. Ingestar corpus inicial

```bash
cd backend
pip install -r requirements.txt
python scripts/bootstrap_corpus.py
```

### 4. Iniciar desarrollo

```bash
# Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Frontend (otra terminal)
cd frontend
npm install
npm run dev
```

### 5. Abrir http://localhost:3000

## Estructura

```
regbot-chile/
├── backend/           # FastAPI + orquestador + ingesta
│   ├── app/
│   │   ├── api/       # Endpoints (chat, health, admin)
│   │   ├── orchestrator/  # Intent, planner, retriever, generator, verifier
│   │   ├── ingestion/     # Scrapers, parser, chunker
│   │   ├── models/        # SQLAlchemy models
│   │   ├── prompts/       # Prompts en .md
│   │   └── utils/         # Claude client, embeddings, cache
│   ├── jobs/          # Scheduler, reindex, refresh
│   ├── tests/         # Tests unitarios y e2e
│   └── scripts/       # Bootstrap, evaluación
├── frontend/          # Next.js 14
│   ├── app/           # App Router pages
│   ├── components/    # Chat, Message, CitationCard, etc.
│   └── lib/           # API client
├── data/              # Golden QA dataset
└── docs/              # Arquitectura, fuentes, legal
```

## Deploy en Railway

### 1. Crear proyecto en Railway

Ir a [railway.app](https://railway.app) y crear un nuevo proyecto.

### 2. Agregar PostgreSQL

- Click "New" > "Database" > "PostgreSQL"
- Railway provee `DATABASE_URL` automáticamente

### 3. Desplegar backend

- Click "New" > "GitHub Repo" > seleccionar este repo
- Root Directory: `backend`
- Variables de entorno requeridas:
  - `ANTHROPIC_API_KEY`
  - `OPENAI_API_KEY`
  - `DATABASE_URL` (se conecta automáticamente al PostgreSQL de Railway)
- Habilitar extensión pgvector: conectarse a la DB y ejecutar `CREATE EXTENSION IF NOT EXISTS vector;`

### 4. Desplegar frontend

- Click "New" > "GitHub Repo" > seleccionar este repo
- Root Directory: `frontend`
- Variables de entorno:
  - `NEXT_PUBLIC_API_URL` = URL pública del backend (ej: `https://backend-xxx.up.railway.app`)
  - `BACKEND_INTERNAL_URL` = URL interna del backend (ej: `http://backend.railway.internal:8000`)

### 5. (Opcional) Agregar Redis

- Click "New" > "Database" > "Redis"
- Agregar `REDIS_URL` al backend (Railway la provee automáticamente)

### Notas Railway

- PostgreSQL de Railway soporta pgvector (ejecutar `CREATE EXTENSION vector` una vez)
- El backend usa `$PORT` automáticamente (Railway lo inyecta)
- Redis es opcional: sin él, el cache se desactiva pero todo funciona
- Las URLs internas (`*.railway.internal`) son gratis y más rápidas entre servicios

## Tests

```bash
cd backend
pytest --cov
```

## Licencia

Proyecto privado.
