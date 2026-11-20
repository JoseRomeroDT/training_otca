#!/usr/bin/env bash
# Detiene y elimina los contenedores del entorno de laboratorio (incluido el gateway del Lab 9).
# La configuración activa del Collector (./active) se conserva.
# Uso: labs/lab-env/down.sh
set -euo pipefail
cd "$(dirname "$0")"
docker compose --profile gateway down
