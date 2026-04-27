# ReguBot Chile

Chatbot con IA que explica la regulación financiera chilena en lenguaje simple, con citas verificadas a fuentes oficiales.

**Demo:** https://regubot-chile-production.up.railway.app/

## Stack

| Capa | Tecnología |
|------|-----------|
| Frontend | Next.js 14 + TypeScript + Tailwind CSS |
| Backend | FastAPI (Python 3.11+) |
| LLM | Claude Haiku 4.5 (Anthropic) con tool use |
| Embeddings | OpenAI text-embedding-3-large (3072 dims) |
| Base de datos | PostgreSQL (embeddings como JSONB) |
| Deploy | Railway (servicio único backend+frontend) |

## Requisitos previos

- [Node.js](https://nodejs.org/) 20+
- [Python](https://python.org/) 3.11+
- API key de [Anthropic](https://console.anthropic.com/) (Claude)
- API key de [OpenAI](https://platform.openai.com/) (embeddings)

---

## Desarrollo local

### 1. Clonar y configurar

```bash
git clone https://github.com/feldivia/regubot-chile.git
cd regubot-chile
cp .env.example .env
# Editar .env con tus API keys (ANTHROPIC_API_KEY, OPENAI_API_KEY)
```

### 2. Levantar base de datos

```bash
docker compose up -d
```

Esto levanta PostgreSQL y Redis (opcional) en local.

### 3. Instalar dependencias

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend (otra terminal)
cd frontend
npm install
```

### 4. Poblar base de datos

```bash
cd backend
python scripts/seed_demo.py
```

Esto inserta 5 leyes chilenas con 17 artículos y genera embeddings con OpenAI.

### 5. Iniciar desarrollo

```bash
# Backend (terminal 1)
cd backend
uvicorn app.main:app --reload --port 8000

# Frontend (terminal 2)
cd frontend
npm run dev
```

### 6. Abrir http://localhost:3000

---

## Deploy en Railway

### Opción A: Desde el dashboard (manual)

1. **Crear proyecto** en [railway.app](https://railway.app)
2. **Agregar PostgreSQL:** New → Database → PostgreSQL
3. **Agregar servicio:** New → GitHub Repo → seleccionar `regubot-chile`
4. **Configurar variables de entorno** en el servicio:
   - `ANTHROPIC_API_KEY` — tu API key de Anthropic
   - `OPENAI_API_KEY` — tu API key de OpenAI
   - `DATABASE_URL` — se conecta automáticamente al PostgreSQL
5. **Esperar deploy** — Railway detecta el Dockerfile y construye automáticamente
6. **Poblar datos:** ejecutar el seed (ver sección siguiente)

### Opción B: Con Railway CLI (automatizado)

Instalar Railway CLI:

```bash
npm install -g @railway/cli
railway login
```

Ejecutar el script de setup:

```bash
./setup-railway.sh
```

O paso a paso:

```bash
# Crear proyecto
railway init --name regubot-chile

# Agregar PostgreSQL
railway add --plugin postgresql

# Vincular al proyecto
railway link

# Configurar variables de entorno
railway variables set ANTHROPIC_API_KEY=sk-ant-...
railway variables set OPENAI_API_KEY=sk-proj-...

# Deploy
railway up

# Poblar la base de datos (requiere URL pública de PostgreSQL)
# Habilitar "Public Networking" en el servicio PostgreSQL desde el dashboard
# Luego:
railway run --service <nombre-servicio> python backend/scripts/seed_demo.py
```

### Poblar la base de datos en Railway

La forma más simple es ejecutar el seed desde tu máquina conectado a la DB de Railway:

```bash
# Obtener la URL pública de PostgreSQL desde el dashboard de Railway
# (Servicio PostgreSQL → Settings → Networking → Public Networking → Enable)

export DATABASE_URL="postgresql://postgres:<password>@<host>:<port>/railway"
export OPENAI_API_KEY="sk-proj-..."

cd backend
python scripts/seed_demo.py
```

---

## Estructura del proyecto

```
regubot-chile/
├── backend/
│   ├── app/
│   │   ├── api/            # Endpoints (chat, health, admin)
│   │   ├── orchestrator/   # Intent, planner, retriever, generator, verifier
│   │   ├── ingestion/      # Scrapers, parser, chunker
│   │   ├── models/         # SQLAlchemy models (norma, articulo, chunk)
│   │   ├── prompts/        # Prompts del sistema en .md
│   │   └── utils/          # Claude client, embeddings, cache
│   ├── scripts/            # seed_demo.py, bootstrap_corpus.py
│   └── tests/
├── frontend/
│   ├── app/                # Next.js App Router
│   ├── components/         # Chat, Message, CitasPanel, etc.
│   └── lib/                # API client
├── docs/                   # Arquitectura, errores, datos disponibles
├── Dockerfile              # Build unificado (backend + frontend)
├── start.sh                # Script de inicio del contenedor
└── docker-compose.yml      # PostgreSQL + Redis para dev local
```

## Datos disponibles

El chatbot tiene información de 5 leyes chilenas (17 artículos):

| Ley | Nombre | Artículos |
|-----|--------|-----------|
| 19.496 | Protección del Consumidor | 1, 3, 12, 16 |
| 21.521 | Ley Fintec | 1, 2, 5, 12 |
| 18.045 | Mercado de Valores | 1, 4, 9, 164, 165 |
| 18.010 | Operaciones de Crédito | 1, 6, 8 |
| 20.345 | Sistemas de Pago | 1 |

Ver detalle completo en [`docs/DATOS_DISPONIBLES.md`](docs/DATOS_DISPONIBLES.md).

## Documentación

| Documento | Contenido |
|-----------|-----------|
| [`docs/DATOS_DISPONIBLES.md`](docs/DATOS_DISPONIBLES.md) | Leyes y artículos en la base de datos |
| [`docs/AVANCE.md`](docs/AVANCE.md) | Estado del proyecto y pendientes |
| [`docs/ERRORES.md`](docs/ERRORES.md) | Registro de errores y soluciones |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Arquitectura técnica |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | Decisiones de diseño |

## Tests

```bash
cd backend
pytest --cov
```

## Licencia

Proyecto privado.
