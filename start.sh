#!/bin/bash
set -e

PORT=${PORT:-8000}
FRONTEND_PORT=3000

# Iniciar frontend Next.js en background
cd /app/frontend
HOSTNAME=0.0.0.0 PORT=$FRONTEND_PORT node server.js &

# Esperar a que Next.js levante
echo "Esperando a que Next.js inicie en puerto $FRONTEND_PORT..."
for i in $(seq 1 30); do
  if curl -sf http://127.0.0.1:$FRONTEND_PORT > /dev/null 2>&1; then
    echo "Next.js listo"
    break
  fi
  sleep 1
done

# Iniciar backend FastAPI en foreground
cd /app/backend
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
