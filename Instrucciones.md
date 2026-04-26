# RegBot Chile — Especificación Técnica para Claude Code

> **Propósito:** Construir un chatbot con IA que convierte la regulación financiera chilena (hoy enterrada en PDFs legales, portales desconectados y lenguaje de abogado) en respuestas que cualquier persona puede entender, verificadas en tiempo real contra datos oficiales.

---

## 1. Contexto y objetivo

### 1.1 Problema
La normativa financiera chilena está dispersa entre múltiples organismos (CMF, Banco Central, SII, Superintendencia de Pensiones, SERNAC), publicada en PDFs y portales desconectados, y escrita en lenguaje técnico-legal inaccesible para el consumidor final.

### 1.2 Usuario objetivo (V1)
Consumidor final: personas comunes con dudas cotidianas sobre sus derechos financieros, cobros bancarios, créditos, tarjetas, cuentas de ahorro, APV, tributación básica, etc.

### 1.3 Propuesta de valor
1. **Respuestas en lenguaje simple** a preguntas regulatorias complejas.
2. **Trazabilidad total:** cada respuesta cita la norma específica con link al texto original.
3. **Datos en vivo:** integración con APIs oficiales para cifras que cambian (UF, UTM, TPM, TMC, etc.).
4. **Validación anti-alucinación:** capa que verifica que las normas citadas existen y están vigentes.

### 1.4 Alcance V1
Cobertura amplia pero superficial del ecosistema regulatorio + datos en vivo para las 6-8 cifras financieras que concentran el 80% de las consultas ciudadanas.

### 1.5 Lo que NO es V1
- Asesoría legal personalizada (disclaimer explícito).
- Jurisprudencia o dictámenes profundos.
- Consultas transaccionales (no se conecta a bancos).
- Usuario profesional (contadores, abogados) — eso es V2.

---

## 2. Stack técnico

| Capa | Tecnología | Justificación |
|---|---|---|
| Frontend | Next.js 14 (App Router) + TypeScript + Tailwind | Streaming nativo, SSR, mobile-first |
| UI components | shadcn/ui + lucide-react | Base sólida, personalizable |
| Backend | FastAPI (Python 3.11+) | Async nativo, buen ecosistema NLP |
| LLM | Claude (modelo `claude-opus-4-7` o superior) vía API de Anthropic | Contextos largos, citas precisas, razonamiento normativo |
| Vector store | PostgreSQL + pgvector | Simple, transaccional, self-hosted |
| Embeddings | `voyage-law-2` (Voyage AI, optimizado para dominio legal) o `text-embedding-3-large` de OpenAI como fallback |
| Orquestación | Código propio en Python (evitar abstracciones pesadas tipo LangChain) |
| Scraping | `httpx` + `selectolax` + `pypdf` / `pdfplumber` |
| Jobs programados | APScheduler o cron + Celery si escala |
| Cache | Redis (respuestas de APIs en vivo + rate limiting) |
| Observabilidad | Logfire o OpenTelemetry + Sentry |
| Deploy | Docker + Fly.io o Railway (V1), migrar a AWS si crece |

---

## 3. Arquitectura

```
┌────────────────────────────────────────────────────────────────┐
│  FRONTEND (Next.js)                                             │
│  - Chat UI con streaming                                        │
│  - Tarjetas de trazabilidad por cada cita                       │
│  - Mobile-first, accesible (WCAG AA)                            │
└────────────────────────────────────────────────────────────────┘
                            │ HTTPS + SSE
                            ▼
┌────────────────────────────────────────────────────────────────┐
│  API GATEWAY (FastAPI)                                          │
│  - Auth opcional (rate limit por IP en V1)                      │
│  - Logging estructurado de todas las queries                    │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│  ORQUESTADOR                                                    │
│  1. Intent classifier (¿normativa? ¿cifra viva? ¿mixto?)        │
│  2. Query planner (qué fuentes consultar)                       │
│  3. Retrieval (RAG + APIs en vivo en paralelo)                  │
│  4. Generación con Claude + tool use                            │
│  5. Verification layer (valida citas antes de responder)        │
│  6. Formateo final con tarjetas de trazabilidad                 │
└────────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  RAG NORMATIVO   │  │  DATOS EN VIVO   │  │  VERIFICADOR     │
│  pgvector        │  │  - BCCh API      │  │  - ¿Norma exists?│
│  + metadata      │  │  - CMF TMC       │  │  - ¿Vigente hoy? │
│  estructurada    │  │  - SII (UTM)     │  │  - ¿Paráfrasis   │
│                  │  │  - Cache Redis   │  │    fiel?         │
└──────────────────┘  └──────────────────┘  └──────────────────┘
          ▲
          │
┌────────────────────────────────────────────────────────────────┐
│  PIPELINE DE INGESTA (jobs diarios/semanales)                   │
│  - Scrapers por fuente con detección de cambios (hash SHA256)   │
│  - Parser que preserva jerarquía (Ley > Título > Art > Numeral) │
│  - Chunking estructural (no arbitrario)                         │
│  - Generación de embeddings                                     │
│  - Marcado de vigencia y relaciones (deroga/modifica)           │
└────────────────────────────────────────────────────────────────┘
```

---

## 4. Estructura del repositorio

```
regbot-chile/
├── README.md
├── docker-compose.yml
├── .env.example
├── pyproject.toml
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entrypoint
│   │   ├── config.py               # Settings (pydantic-settings)
│   │   ├── api/
│   │   │   ├── chat.py             # POST /chat (streaming)
│   │   │   ├── health.py
│   │   │   └── admin.py            # Reindex, estadísticas
│   │   ├── orchestrator/
│   │   │   ├── intent.py           # Clasificador de intención
│   │   │   ├── planner.py          # Decide fuentes a consultar
│   │   │   ├── retriever.py        # RAG con pgvector
│   │   │   ├── live_data.py        # Llamadas a APIs en vivo
│   │   │   ├── generator.py        # Prompt + Claude + tool use
│   │   │   ├── verifier.py         # Capa de verificación
│   │   │   └── formatter.py        # Tarjetas de trazabilidad
│   │   ├── ingestion/
│   │   │   ├── base.py             # Clase abstracta Scraper
│   │   │   ├── leychile.py         # Scraper leychile.cl
│   │   │   ├── cmf.py              # Scraper CMF
│   │   │   ├── sii.py              # Scraper SII
│   │   │   ├── bcch.py             # API Banco Central
│   │   │   ├── sp.py               # Superintendencia de Pensiones
│   │   │   ├── sernac.py
│   │   │   ├── parser.py           # Parser normativo (jerarquía)
│   │   │   └── chunker.py          # Chunking estructural
│   │   ├── models/
│   │   │   ├── norma.py            # SQLAlchemy: Ley, Articulo, etc.
│   │   │   ├── chunk.py            # Chunk con embedding
│   │   │   └── query_log.py        # Auditoría de queries
│   │   ├── db/
│   │   │   ├── session.py
│   │   │   └── migrations/         # Alembic
│   │   ├── prompts/
│   │   │   ├── system.md           # Prompt de sistema principal
│   │   │   ├── intent.md
│   │   │   ├── verifier.md
│   │   │   └── formatter.md
│   │   └── utils/
│   │       ├── claude_client.py
│   │       ├── embeddings.py
│   │       └── cache.py            # Redis wrapper
│   ├── jobs/
│   │   ├── scheduler.py            # APScheduler config
│   │   ├── reindex_daily.py
│   │   └── refresh_live_data.py
│   ├── tests/
│   │   ├── test_ingestion/
│   │   ├── test_orchestrator/
│   │   └── test_e2e/
│   └── scripts/
│       ├── bootstrap_corpus.py     # Ingesta inicial completa
│       └── eval_qa.py              # Evaluación con dataset dorado
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                # Landing + chat
│   │   └── api/
│   │       └── chat/route.ts       # Proxy a backend (streaming)
│   ├── components/
│   │   ├── Chat.tsx
│   │   ├── Message.tsx
│   │   ├── CitationCard.tsx        # Tarjeta de trazabilidad
│   │   ├── LiveDataBadge.tsx       # "UF de hoy: $37.xxx"
│   │   └── Disclaimer.tsx
│   └── lib/
│       └── api.ts
├── data/
│   ├── golden_qa.jsonl             # Dataset de evaluación
│   └── seeds/                      # Normas prioritarias V1
└── docs/
    ├── ARCHITECTURE.md
    ├── SOURCES.md                  # Catálogo de fuentes
    ├── PROMPTING.md
    └── LEGAL.md                    # Disclaimers y política
```

---

## 5. Fuentes de datos

### 5.1 Normativa (RAG)

**Tier 1 — obligatorio V1:**

| Fuente | URL base | Método | Frecuencia |
|---|---|---|---|
| leychile.cl | `https://www.bcn.cl/leychile/` | API + scraping | Semanal |
| CMF — Normativa | `https://www.cmfchile.cl/portal/principal/613/w3-propertyvalue-18405.html` | Scraping | Semanal |
| Banco Central — Compendio Normas Financieras | `https://www.bcentral.cl/web/banco-central/normativa` | Scraping PDF | Mensual |

**Leyes prioritarias a ingestar primero:**
- Ley 19.496 (Protección del Consumidor, incluye Consumidor Financiero)
- Ley 21.521 (Fintec)
- Ley 20.712 (Administración de Fondos)
- Ley 18.010 (Operaciones de Crédito de Dinero — tasa máxima convencional)
- Ley 18.045 (Mercado de Valores)
- Ley 18.046 (Sociedades Anónimas)
- Ley 20.345 (Sistemas de Pagos)
- DL 3.500 (Sistema de Pensiones)
- Ley 21.000 (Comisión para el Mercado Financiero)

**Tier 2 — semana 2-3:**

| Fuente | URL | Método |
|---|---|---|
| SII — Normativa | `https://www.sii.cl/normativa_legislacion/` | Scraping |
| Superintendencia de Pensiones | `https://www.spensiones.cl/portal/institucional/594/w3-propertyvalue-6114.html` | Scraping |
| SERNAC | `https://www.sernac.cl/portal/619/w3-propertyvalue-76016.html` | Scraping selectivo |

### 5.2 Datos en vivo (APIs)

| Dato | Fuente | Endpoint | Frecuencia |
|---|---|---|---|
| UF | Banco Central (si3.bcentral.cl) | Serie `F073.UFF.PRE.Z.D` | Diaria |
| UTM | SII + BCCh | `UTMU` serie | Mensual |
| TPM | Banco Central | Serie `F022.TPM.TIN.D001.NO.Z.D` | Eventos monetarios |
| Tasa Máxima Convencional | CMF | `https://www.cmfchile.cl/portal/estadisticas/606/w3-propertyvalue-28658.html` | Quincenal |
| Dólar observado | Banco Central | Serie `F073.TCO.PRE.Z.D` | Diaria |
| IPC | INE vía BCCh | Serie `F074.IPC.VAR.Z.Z.M` | Mensual |
| Sueldo mínimo | Dirección del Trabajo | Hardcode + actualización manual | Anual |

**Nota:** El Banco Central requiere registro gratuito para la API. Credenciales en `.env`.

---

## 6. Modelo de datos

### 6.1 Esquema principal

```sql
-- Norma jurídica (cabecera)
CREATE TABLE norma (
  id              UUID PRIMARY KEY,
  tipo            VARCHAR(50) NOT NULL,   -- 'ley', 'decreto', 'ncg', 'circular'
  numero          VARCHAR(50),
  titulo          TEXT NOT NULL,
  organismo       VARCHAR(100) NOT NULL,  -- 'CMF', 'BCCh', 'SII', 'Congreso'
  fecha_publicacion DATE,
  fecha_vigencia  DATE,
  derogada        BOOLEAN DEFAULT FALSE,
  fecha_derogacion DATE,
  url_oficial     TEXT NOT NULL,
  hash_contenido  VARCHAR(64) NOT NULL,   -- SHA256 para detectar cambios
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Artículo o sección estructural
CREATE TABLE articulo (
  id              UUID PRIMARY KEY,
  norma_id        UUID REFERENCES norma(id) ON DELETE CASCADE,
  path            TEXT NOT NULL,  -- ej. "Titulo II > Capitulo 3 > Art 17 B"
  numero          VARCHAR(20),
  texto           TEXT NOT NULL,
  orden           INT NOT NULL,
  vigente         BOOLEAN DEFAULT TRUE
);

-- Relaciones entre normas (modifica, deroga, reglamenta)
CREATE TABLE relacion_norma (
  id              UUID PRIMARY KEY,
  norma_origen    UUID REFERENCES norma(id),
  norma_destino   UUID REFERENCES norma(id),
  tipo_relacion   VARCHAR(20)  -- 'modifica', 'deroga', 'reglamenta', 'cita'
);

-- Chunks vectorizados para RAG
CREATE TABLE chunk (
  id              UUID PRIMARY KEY,
  articulo_id     UUID REFERENCES articulo(id) ON DELETE CASCADE,
  texto           TEXT NOT NULL,
  embedding       vector(1024),  -- ajustar según modelo
  metadata        JSONB,
  tokens          INT
);

CREATE INDEX chunk_embedding_idx ON chunk USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX chunk_metadata_idx ON chunk USING gin (metadata);

-- Log de consultas para auditoría y mejora
CREATE TABLE query_log (
  id              UUID PRIMARY KEY,
  session_id      UUID,
  pregunta        TEXT NOT NULL,
  respuesta       TEXT NOT NULL,
  citas           JSONB,
  datos_vivos     JSONB,
  verificacion_pasada BOOLEAN,
  latencia_ms     INT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 7. Flujo de una consulta

Ejemplo: usuario pregunta *"¿Puedo pagar anticipadamente mi crédito de consumo sin multa?"*

1. **Intent classifier** → detecta intención normativa (Ley del Consumidor Financiero + Ley 18.010).
2. **Query planner** → decide consultar RAG normativo + no requiere datos en vivo.
3. **Retrieval** → pgvector devuelve top-k chunks. Se priorizan chunks marcados `vigente=TRUE`.
4. **Generación** → Claude recibe los chunks + pregunta + prompt de sistema. Produce respuesta con citas formateadas como `[CITA:articulo_id]`.
5. **Verificación** → para cada `[CITA:id]`:
   - Existe en DB.
   - `vigente=TRUE` y `derogada=FALSE`.
   - Similitud semántica respuesta-vs-texto original > umbral (anti-contradicción).
6. **Formateo** → se reemplazan `[CITA:id]` por tarjetas renderizadas con link a `url_oficial`.
7. **Respuesta streaming** al frontend + log a `query_log`.

---

## 8. Prompt de sistema (borrador)

Archivo: `backend/app/prompts/system.md`

```markdown
Eres RegBot, un asistente que explica la regulación financiera chilena a personas comunes.

## Principios innegociables
1. **Nunca inventes normas.** Solo cita las que aparezcan en el contexto entregado.
2. **Responde en lenguaje simple.** Nada de "conforme a lo dispuesto en el artículo". Di "la ley dice que...".
3. **Cita siempre la fuente** con el formato `[CITA:<articulo_id>]` después de cada afirmación factual.
4. **Si no sabes, dilo.** "No tengo información suficiente sobre eso en la normativa vigente."
5. **Nunca des asesoría legal personalizada.** Explica la norma, no qué debe hacer el usuario.
6. **Si la consulta involucra montos grandes, disputas o juicios**, sugiere consultar abogado o SERNAC.

## Formato de respuesta
- Máximo 4-5 párrafos cortos.
- Empieza con la respuesta directa en 1-2 frases.
- Luego el detalle con citas.
- Si hay una cifra viva relevante (UF, TMC, etc.), úsala usando el tool `obtener_dato_vivo`.

## Datos en vivo disponibles vía tool use
- `obtener_uf(fecha?)`
- `obtener_utm(mes?)`
- `obtener_tmc(tramo)`
- `obtener_tpm()`
- `obtener_dolar_observado(fecha?)`
- `obtener_ipc(mes?)`

## Lo que NO debes hacer
- Nunca afirmar que algo es legal/ilegal sin citar norma.
- Nunca opinar sobre la justicia o conveniencia de una norma.
- Nunca recomendar un producto financiero específico.
```

---

## 9. Fases de implementación

### Fase 0 — Setup (día 1-2)
- [ ] Monorepo con `backend/` y `frontend/`.
- [ ] Docker Compose con Postgres+pgvector y Redis.
- [ ] CI básico (lint, tests).
- [ ] `.env.example` con todas las variables.

### Fase 1 — Ingesta base (semana 1)
- [ ] Scraper de leychile.cl con las 9 leyes prioritarias.
- [ ] Parser que preserva jerarquía (Titulo/Capitulo/Articulo).
- [ ] Chunking estructural (nunca parte un artículo a la mitad si cabe).
- [ ] Generación de embeddings.
- [ ] Script `bootstrap_corpus.py` idempotente.

### Fase 2 — RAG + Claude (semana 2)
- [ ] Endpoint `POST /chat` con streaming (SSE).
- [ ] Retriever híbrido (vectorial + BM25 sobre título/número de norma).
- [ ] Prompt de sistema v1.
- [ ] Integración Claude con tool use.
- [ ] Frontend chat mínimo.

### Fase 3 — Datos en vivo (semana 3)
- [ ] Cliente API Banco Central (UF, UTM, TPM, dólar, IPC).
- [ ] Scraper CMF para TMC.
- [ ] Cache en Redis (TTL por tipo de dato).
- [ ] Tools expuestos a Claude.
- [ ] Job de refresh cada 1h para TMC, 15min para TPM eventos.

### Fase 4 — Verificación + UX (semana 4)
- [ ] Verification layer completo.
- [ ] Tarjetas de trazabilidad en frontend.
- [ ] Disclaimer persistente.
- [ ] Dataset dorado de 50 Q&A para eval.
- [ ] Script `eval_qa.py` con métricas: faithfulness, citation accuracy, helpfulness.

### Fase 5 — Tier 2 fuentes (semana 5)
- [ ] Scrapers SII, SP, SERNAC.
- [ ] Re-ingesta corpus ampliado.
- [ ] Tuning de retrieval con nuevo volumen.

### Fase 6 — Hardening y lanzamiento (semana 6)
- [ ] Rate limiting por IP.
- [ ] Observabilidad completa (logs estructurados, métricas).
- [ ] Pruebas con 10-20 usuarios beta.
- [ ] Fix de issues críticos.
- [ ] Deploy producción.

---

## 10. Criterios de aceptación (Definition of Done V1)

### Funcionales
- Usuario puede hacer una pregunta en lenguaje natural y recibir respuesta en < 8 segundos (p95).
- 100% de las afirmaciones factuales llevan cita verificable a fuente oficial.
- Respuestas usan datos en vivo cuando corresponde (UF actual, TMC vigente, etc.).
- El bot rechaza adecuadamente preguntas fuera de alcance (salud, penal, etc.).

### Calidad normativa
- En un dataset dorado de 50 preguntas:
  - ≥ 90% de citas apuntan a norma correcta.
  - 0% de citas a normas derogadas.
  - ≥ 85% de respuestas evaluadas como "útiles y comprensibles" por 3 revisores.

### Técnicos
- Cobertura de tests > 70% en backend.
- Deploy automatizado desde `main`.
- Re-ingesta de corpus completa corre en < 30 minutos.
- Detección automática de cambios en normas (hash diff).

### Legales/UX
- Disclaimer visible en cada respuesta y en landing.
- Cada cita enlaza al texto oficial en leychile.cl / portal CMF.
- Política de derivación a profesional cuando aplique.
- Log de todas las consultas para auditoría (sin PII identificable).

---

## 11. Variables de entorno

```bash
# .env.example
ANTHROPIC_API_KEY=
VOYAGE_API_KEY=
BCCH_USER=
BCCH_PASSWORD=
DATABASE_URL=postgresql://regbot:regbot@localhost:5432/regbot
REDIS_URL=redis://localhost:6379/0
SENTRY_DSN=
LOG_LEVEL=INFO
RATE_LIMIT_PER_MIN=20
CLAUDE_MODEL=claude-opus-4-7
EMBEDDING_MODEL=voyage-law-2
```

---

## 12. Notas para Claude Code

- **Empieza por la Fase 0 y 1.** No avances a retrieval/LLM hasta tener corpus indexado de al menos 3 leyes.
- **Prioriza idempotencia en scrapers.** Correr el mismo scraper 10 veces debe dar el mismo resultado.
- **Cada PR debe incluir tests.** Especialmente para el parser normativo (es la pieza más crítica y frágil).
- **No uses LangChain ni LlamaIndex.** Código propio, control explícito.
- **Los prompts van en archivos `.md` separados**, no hardcodeados en Python.
- **Errores visibles ≠ errores silenciosos.** Si un scraper falla, log estructurado + Sentry, nunca swallow.
- **Todo el código, docstrings y comentarios en español** (excepto términos técnicos estándar como "embedding", "chunk", "retriever").
- **Cuando encuentres ambigüedad en el spec**, asume el camino más simple que cumpla el criterio de aceptación, documenta la decisión en `docs/DECISIONS.md`, y continúa.

---

## 13. Riesgos conocidos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Scraper se rompe por cambio en portal CMF/SII | Alto | Tests contract-based, alertas por volumen inesperado, reintento manual |
| Claude alucina citas a normas inexistentes | Crítico | Verification layer obligatoria, rechazar respuesta si falla |
| Usuario toma decisión financiera basada en error del bot | Crítico | Disclaimer visible, derivación a profesional, logs de auditoría |
| Corpus crece y retrieval pierde precisión | Medio | Reranker (Cohere Rerank o similar) en Fase 7 |
| Costos de Claude explotan | Medio | Cache de respuestas a preguntas frecuentes (normalización semántica) |
| Cambio legal mayor (nueva ley Fintec) no detectado | Alto | Job diario de diff + notificación a mantenedor |

---

## 14. Próximos pasos post-V1 (no implementar ahora)

- Perfil "profesional" con vista avanzada (texto completo, historial de modificaciones).
- Integración con jurisprudencia relevante.
- Alertas personalizadas ("avísame si cambia la tasa máxima").
- API pública para terceros.
- Modo offline con modelo local para preguntas frecuentes.
- Multi-idioma (inglés para inversionistas extranjeros).

---

**Fin del brief. Éxito, Claude Code.**