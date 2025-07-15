#!/bin/bash
echo "🚀 Iniciando ProManage..."

# Desarrollo
echo "Modo: Desarrollo"
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

