# CLAUDE.md - Instrucciones para Claude Code

## Proyecto
ReguBot Chile: chatbot de regulacion financiera chilena con RAG + Claude.

## Archivos criticos a consultar SIEMPRE

### Antes de cualquier cambio
- **`docs/ERRORES.md`** - Registro de errores y soluciones. Consultar ANTES de modificar configuracion de deploy, infraestructura o dependencias. Evita repetir errores ya resueltos.
- **`docs/AVANCE.md`** - Estado actual del proyecto, que esta hecho, que falta. Actualizar despues de completar tareas significativas.
- **`Instrucciones.md`** - Spec tecnico completo del proyecto. Referencia para decisiones de arquitectura.

## Reglas del proyecto

### Codigo
- Todo el codigo, docstrings y comentarios en espanol (excepto terminos tecnicos: embedding, chunk, retriever, etc.)
- No usar LangChain ni LlamaIndex. Codigo propio, control explicito.
- Los prompts van en archivos `.md` separados en `backend/app/prompts/`, nunca hardcodeados.
- Errores visibles, nunca silenciosos. Si un scraper falla: log estructurado, nunca swallow.
- Scrapers deben ser idempotentes (correr 10 veces = mismo resultado).

### Deploy
- Railway es la plataforma de deploy. El Dockerfile debe estar en la RAIZ del repo.
- Railway usa Railpack como builder. Railpack ignora nixpacks.toml y railpack.toml. Solo detecta Dockerfile de forma confiable.
- DATABASE_URL de Railway usa prefijo `postgresql://`. La app lo convierte a `postgresql+asyncpg://` automaticamente en `db/session.py`.
- Redis es OPCIONAL. La app funciona sin el (cache desactivado).
- BCCh API es OPCIONAL. Sin credenciales, datos en vivo del Banco Central no estan disponibles pero no rompe nada.

### Modelos
- LLM: Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) - modelo economico
- Embeddings: OpenAI `text-embedding-3-large` (3072 dimensiones)

### Workflow
- Cuando resuelvas un error significativo, documentarlo en `docs/ERRORES.md`
- Cuando completes una tarea, actualizar `docs/AVANCE.md`
- Ante ambiguedad en el spec, asumir el camino mas simple y documentar en `docs/DECISIONS.md`
