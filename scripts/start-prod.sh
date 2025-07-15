#!/bin/bash
echo "🚀 Iniciando ProManage (Producción)..."

# Producción
docker-compose up --build -d

echo "✅ Aplicación corriendo en:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   Docs:     http://localhost:8000/docs"

