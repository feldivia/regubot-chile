#!/bin/bash
set -e

PORT=${PORT:-8000}
FRONTEND_PORT=3000

# Iniciar frontend Next.js en background
cd /app/frontend
HOSTNAME=0.0.0.0 PORT=$FRONTEND_PORT node server.js &

# Iniciar backend FastAPI en foreground
cd /app/backend
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
