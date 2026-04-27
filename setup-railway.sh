#!/bin/bash
# Setup automatizado de ReguBot Chile en Railway
# Requisitos: railway CLI instalado y autenticado (railway login)
set -e

echo "=== ReguBot Chile - Setup Railway ==="
echo ""

# Verificar railway CLI
if ! command -v railway &> /dev/null; then
    echo "Error: Railway CLI no encontrado."
    echo "Instalar con: npm install -g @railway/cli"
    echo "Luego: railway login"
    exit 1
fi

# Verificar login
if ! railway whoami &> /dev/null; then
    echo "Error: No autenticado en Railway."
    echo "Ejecutar: railway login"
    exit 1
fi

echo "Railway CLI OK: $(railway whoami 2>/dev/null)"
echo ""

# Verificar API keys
if [ -z "$ANTHROPIC_API_KEY" ]; then
    read -p "ANTHROPIC_API_KEY: " ANTHROPIC_API_KEY
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        echo "Error: ANTHROPIC_API_KEY es requerida"
        exit 1
    fi
fi

if [ -z "$OPENAI_API_KEY" ]; then
    read -p "OPENAI_API_KEY: " OPENAI_API_KEY
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "Error: OPENAI_API_KEY es requerida"
        exit 1
    fi
fi

echo ""
echo "1/5 - Creando proyecto en Railway..."
railway init --name regubot-chile 2>/dev/null || echo "  (proyecto ya existe, vinculando...)"
railway link --project regubot-chile 2>/dev/null || true

echo ""
echo "2/5 - Agregando PostgreSQL..."
echo "  NOTA: Si el plugin ya existe, este paso se salta."
railway add --plugin postgresql 2>/dev/null || echo "  (PostgreSQL ya existe)"

echo ""
echo "3/5 - Configurando variables de entorno..."
railway variables set \
    ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
    OPENAI_API_KEY="$OPENAI_API_KEY" \
    LOG_LEVEL=INFO \
    CLAUDE_MODEL=claude-haiku-4-5-20251001 \
    EMBEDDING_MODEL=text-embedding-3-large \
    2>/dev/null

echo "  Variables configuradas."

echo ""
echo "4/5 - Desplegando servicio..."
railway up --detach

echo ""
echo "5/5 - Esperando deploy..."
echo "  El deploy toma ~3-5 minutos."
echo ""
echo "=== Siguientes pasos manuales ==="
echo ""
echo "1. Esperar a que el deploy termine en https://railway.app"
echo ""
echo "2. Habilitar Public Networking en el servicio PostgreSQL:"
echo "   Dashboard → servicio PostgreSQL → Settings → Networking → Enable"
echo ""
echo "3. Poblar la base de datos con los datos de semilla:"
echo "   export DATABASE_URL=<URL_PUBLICA_POSTGRESQL>"
echo "   export OPENAI_API_KEY=$OPENAI_API_KEY"
echo "   cd backend && python scripts/seed_demo.py"
echo ""
echo "4. (Opcional) Deshabilitar Public Networking en PostgreSQL"
echo ""
echo "=== Setup completado ==="
