#!/usr/bin/env bash
# Levanta el entorno de laboratorio: OpenTelemetry Collector + Jaeger + Prometheus.
# Uso: labs/lab-env/up.sh
set -euo pipefail
cd "$(dirname "$0")"

mkdir -p active
if [ ! -f active/collector.yaml ]; then
  cp otelcol-config.yaml active/collector.yaml
  echo "Configuración inicial del Collector: otelcol-config.yaml"
fi

docker compose up -d
echo ""
./status.sh
