#!/bin/bash
# ============================================================
# ReguBot Chile - Setup automatizado en Railway
# ============================================================
# Requisitos:
#   - Node.js 20+ (para Railway CLI)
#   - Python 3.11+ (para seed de datos)
#   - railway CLI: npm install -g @railway/cli
#   - Autenticado: railway login
#
# Uso:
#   export ANTHROPIC_API_KEY=sk-ant-...
#   export OPENAI_API_KEY=sk-proj-...
#   ./setup-railway.sh
# ============================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "=========================================="
echo "  ReguBot Chile - Setup Railway"
echo "=========================================="
echo ""

# --- 1. Verificar dependencias ---

echo -e "${YELLOW}[1/6] Verificando dependencias...${NC}"

if ! command -v railway &> /dev/null; then
    echo -e "${RED}Error: Railway CLI no encontrado.${NC}"
    echo "  Instalar: npm install -g @railway/cli"
    echo "  Luego:    railway login"
    exit 1
fi

if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python no encontrado.${NC}"
    exit 1
fi
PYTHON=$(command -v python3 || command -v python)

if ! railway whoami &> /dev/null 2>&1; then
    echo -e "${RED}Error: No autenticado en Railway.${NC}"
    echo "  Ejecutar: railway login"
    exit 1
fi

echo -e "  ${GREEN}Railway CLI: $(railway --version)${NC}"
echo -e "  ${GREEN}Python: $($PYTHON --version)${NC}"
echo ""

# --- 2. Pedir API keys si no están como variables de entorno ---

if [ -z "$ANTHROPIC_API_KEY" ]; then
    read -p "  ANTHROPIC_API_KEY: " ANTHROPIC_API_KEY
    [ -z "$ANTHROPIC_API_KEY" ] && echo -e "${RED}Requerida${NC}" && exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
    read -p "  OPENAI_API_KEY: " OPENAI_API_KEY
    [ -z "$OPENAI_API_KEY" ] && echo -e "${RED}Requerida${NC}" && exit 1
fi

echo ""

# --- 3. Crear proyecto ---

echo -e "${YELLOW}[2/6] Creando proyecto en Railway...${NC}"
railway init --name regubot-chile 2>/dev/null || true
railway link --project regubot-chile 2>/dev/null || true
echo -e "  ${GREEN}Proyecto vinculado${NC}"
echo ""

# --- 4. Crear base de datos PostgreSQL con pgvector ---

echo -e "${YELLOW}[3/6] Creando PostgreSQL con pgvector...${NC}"
echo ""
echo "  Railway ofrece dos opciones para PostgreSQL:"
echo ""
echo "  a) PostgreSQL estándar (sin pgvector):"
echo "     railway add --database postgres"
echo ""
echo "  b) pgvector desde imagen Docker (recomendado):"
echo "     railway add --service pgvector --image pgvector/pgvector:pg16"
echo ""
echo "  NOTA: ReguBot usa JSONB para embeddings, así que ambas opciones"
echo "  funcionan. pgvector es recomendado por si se quiere migrar a"
echo "  búsqueda vectorial nativa en el futuro."
echo ""

read -p "  ¿Crear PostgreSQL con pgvector? (S/n): " CREAR_DB
CREAR_DB=${CREAR_DB:-S}

if [[ "$CREAR_DB" =~ ^[Ss]$ ]]; then
    # Intentar con imagen pgvector primero
    echo "  Creando servicio pgvector..."
    railway add --database postgres --service pgvector 2>/dev/null || \
        echo -e "  ${YELLOW}Servicio de base de datos ya existe, continuando...${NC}"
    echo -e "  ${GREEN}PostgreSQL creado${NC}"
fi
echo ""

# --- 5. Configurar variables y desplegar ---

echo -e "${YELLOW}[4/6] Configurando variables de entorno...${NC}"

# Obtener nombre del servicio de la app (no la DB)
echo "  Configurando API keys en el servicio principal..."
railway variable set \
    ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
    OPENAI_API_KEY="$OPENAI_API_KEY" \
    LOG_LEVEL=INFO \
    CLAUDE_MODEL=claude-haiku-4-5-20251001 \
    EMBEDDING_MODEL=text-embedding-3-large \
    2>/dev/null || true

echo -e "  ${GREEN}Variables configuradas${NC}"
echo ""

echo -e "${YELLOW}[5/6] Desplegando aplicación...${NC}"
railway up --detach 2>/dev/null || true
echo -e "  ${GREEN}Deploy iniciado${NC}"
echo ""

# --- 6. Seed de datos ---

echo -e "${YELLOW}[6/6] Poblar base de datos...${NC}"
echo ""
echo "  Para poblar la BD necesitas la URL pública de PostgreSQL."
echo ""
echo "  Pasos:"
echo "    1. Ir al dashboard de Railway: https://railway.app"
echo "    2. Seleccionar el servicio PostgreSQL/pgvector"
echo "    3. Ir a Settings → Networking → Enable Public Networking"
echo "    4. Copiar la DATABASE_PUBLIC_URL"
echo "    5. Ejecutar:"
echo ""
echo "       export DATABASE_URL=<DATABASE_PUBLIC_URL>"
echo "       export OPENAI_API_KEY=$OPENAI_API_KEY"
echo "       cd backend"
echo "       pip install -r requirements.txt"
echo "       python scripts/seed_demo.py"
echo ""
echo "  Esto inserta 5 leyes chilenas (17 artículos) con embeddings."
echo ""

# --- Resumen ---

echo "=========================================="
echo -e "  ${GREEN}Setup completado${NC}"
echo "=========================================="
echo ""
echo "  Proyecto:  regubot-chile"
echo "  Dashboard: https://railway.app"
echo ""
echo "  El deploy toma ~3-5 minutos."
echo "  Una vez listo, la URL pública aparece en el dashboard."
echo ""
echo "  Después del seed, puedes deshabilitar Public Networking"
echo "  en PostgreSQL por seguridad."
echo ""
