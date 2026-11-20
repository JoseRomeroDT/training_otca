#!/usr/bin/env bash
# Comprueba que el entorno de laboratorio responde y muestra las URLs de acceso
# (en GitHub Codespaces imprime las URLs públicas del reenvío de puertos).
# Uso: labs/lab-env/status.sh
set -uo pipefail

check() {
  local name="$1" url="$2" i
  for i in 1 2 3 4 5 6 7 8 9 10; do
    if curl -fsS -o /dev/null --max-time 3 "$url"; then
      echo "  OK     $name"
      return 0
    fi
    sleep 2
  done
  echo "  FALLA  $name ($url) -> revisa: docker compose -f labs/lab-env/compose.yaml ps"
  return 1
}

echo "Estado del entorno de laboratorio:"
check "Collector (health_check :13133)" "http://localhost:13133/"
check "Jaeger UI (:16686)"              "http://localhost:16686/"
check "Prometheus (:9090)"              "http://localhost:9090/-/ready"

url() {
  if [ -n "${CODESPACE_NAME:-}" ]; then
    echo "https://${CODESPACE_NAME}-$1.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}$2"
  else
    echo "http://localhost:$1$2"
  fi
}

echo ""
echo "Accesos:"
echo "  Jaeger UI (trazas)      : $(url 16686 /)"
echo "  Prometheus (métricas)   : $(url 9090 /)"
echo "  Collector zPages        : $(url 55679 /debug/tracez)"
echo "  OTLP para tus apps      : gRPC localhost:4317 · HTTP localhost:4318"
echo ""
echo "Logs del Collector: docker logs -f otel-collector"
