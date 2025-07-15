#!/bin/bash
echo "🧹 Limpiando containers y volúmenes..."
docker-compose down -v
docker system prune -f

