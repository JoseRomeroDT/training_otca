#!/usr/bin/env bash
# Valida una configuración del Collector con "otelcol-contrib validate" y, si es
# válida, la activa en el entorno de laboratorio y reinicia el contenedor.
#
# Uso:
#   labs/lab-env/use-collector-config.sh <archivo.yaml>            # Collector principal
#   labs/lab-env/use-collector-config.sh <archivo.yaml> gateway    # gateway del Lab 9
set -euo pipefail
LAB_ENV="$(cd "$(dirname "$0")" && pwd)"
IMAGE="otel/opentelemetry-collector-contrib:0.165.0"
FILE="${1:?Uso: use-collector-config.sh <archivo.yaml> [collector|gateway]}"
TARGET="${2:-collector}"

case "$TARGET" in
  collector|gateway) ;;
  *) echo "El segundo argumento debe ser 'collector' o 'gateway'." >&2; exit 2 ;;
esac
[ -f "$FILE" ] || { echo "No existe el archivo: $FILE" >&2; exit 1; }
ABS="$(cd "$(dirname "$FILE")" && pwd)/$(basename "$FILE")"

echo "==> Validando $FILE"
docker run --rm -v "$ABS:/tmp/config.yaml:ro" "$IMAGE" validate --config=/tmp/config.yaml
echo "    Configuración válida."

mkdir -p "$LAB_ENV/active"
cp "$ABS" "$LAB_ENV/active/$TARGET.yaml"

echo "==> Reiniciando otel-$TARGET con la nueva configuración"
if [ "$TARGET" = "gateway" ]; then
  docker compose -f "$LAB_ENV/compose.yaml" --profile gateway up -d --force-recreate otel-gateway
else
  docker compose -f "$LAB_ENV/compose.yaml" up -d --force-recreate otel-collector
fi
echo "Listo. Revisa los logs con: docker logs -f otel-$TARGET"
