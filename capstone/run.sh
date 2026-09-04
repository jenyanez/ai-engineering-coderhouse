#!/usr/bin/env bash
set -e

echo "============================================================"
echo "🚀 Sistema Intelligence de Grado de Producción (Capstone)"
echo "============================================================"

# Verificar si Docker está disponible
if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo "🐳 Docker detectado y activo. Iniciando servicios con Docker Compose..."
    docker compose up --build -d
    echo ""
    echo "✅ Servicios inicializados:"
    echo "   - API REST FastAPI & Mission Control: http://localhost:8000/docs | http://localhost:8000/dashboard"
    echo "   - Arize Phoenix Dashboard:          http://localhost:6006"
    echo "   - Redis Message Broker & Store:      localhost:6379"
    echo ""
    echo "Para ver logs en tiempo real: docker compose logs -f app"
    echo "Para detener los servicios:   docker compose down"
else
    echo "⚠️ Docker no está corriendo o no está instalado."
    echo "Iniciando en modo local (Python)..."
    
    if [ ! -d ".venv" ]; then
        echo "📦 Creando entorno virtual .venv..."
        python3 -m venv .venv
    fi
    
    source .venv/bin/activate
    echo "📥 Verificando dependencias..."
    pip install -q -r requirements.txt
    
    echo "🚀 Levantando servidor API..."
    python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi
