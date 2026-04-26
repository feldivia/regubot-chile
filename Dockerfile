# --- Stage 1: Build frontend ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
ENV NEXT_TELEMETRY_DISABLED=1
# La API corre en el mismo host, el frontend la accede via /api
ENV NEXT_PUBLIC_API_URL=""
RUN npm run build

# --- Stage 2: Runtime ---
FROM python:3.11-slim

# Instalar Node.js para servir Next.js standalone
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Backend
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .

# Frontend (standalone build)
WORKDIR /app/frontend
COPY --from=frontend-builder /app/.next/standalone ./
COPY --from=frontend-builder /app/.next/static ./.next/static
COPY --from=frontend-builder /app/public ./public 2>/dev/null || true

# Script de inicio
WORKDIR /app
COPY start.sh .
RUN chmod +x start.sh

EXPOSE ${PORT:-8000}

CMD ["./start.sh"]
