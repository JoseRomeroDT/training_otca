#!/usr/bin/env bash
# Vuelve a la configuración "del curso" del Collector y detiene el gateway del Lab 9.
# Uso: labs/lab-env/reset-collector.sh
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p active
cp otelcol-config.yaml active/collector.yaml
docker compose --profile gateway rm --stop --force otel-gateway >/dev/null 2>&1 || true
docker compose up -d --force-recreate otel-collector
echo "Collector restablecido a labs/lab-env/otelcol-config.yaml"
