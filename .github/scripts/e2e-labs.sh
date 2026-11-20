#!/usr/bin/env bash
# Prueba de extremo a extremo del entorno de laboratorio.
# La ejecuta el CI y también sirve en un Codespace: bash .github/scripts/e2e-labs.sh
# Recorre los labs 0, 4, 5, 8, 9 y 11 contra el Collector, Jaeger y Prometheus reales.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
PY="${PYTHON:-python}"

wait_for() {
  local desc="$1"; shift
  for _ in $(seq 1 40); do
    if "$@" >/dev/null 2>&1; then echo "  OK     $desc"; return 0; fi
    sleep 3
  done
  echo "  FALLA  $desc"
  docker ps -a --format 'table {{.Names}}\t{{.Status}}' || true
  echo "--- Jaeger /api/v3/services:"; curl -sS "http://localhost:16686/api/v3/services" || true; echo
  echo "--- jaeger (últimas líneas):"; docker logs jaeger 2>&1 | tail -20 || true
  echo "--- otel-collector (últimas líneas):"; docker logs otel-collector 2>&1 | tail -60 || true
  if docker ps --format '{{.Names}}' | grep -qx otel-gateway; then
    echo "--- otel-gateway (últimas líneas):"; docker logs otel-gateway 2>&1 | tail -40 || true
  fi
  return 1
}
prom_has() {
  curl -fsS --get "http://localhost:9090/api/v1/query" --data-urlencode "query=$1" \
    | "$PY" -c "import sys, json; sys.exit(0 if json.load(sys.stdin)['data']['result'] else 1)"
}
# Jaeger v2 expone la búsqueda en la API v3 (/api/v3/services y /api/v3/traces).
jaeger_has_service() {
  curl -fsS "http://localhost:16686/api/v3/services" \
    | "$PY" -c "import sys, json; sys.exit(0 if sys.argv[1] in (json.load(sys.stdin).get('services') or []) else 1)" "$1"
}
# Se lee la salida completa antes de buscar: con pipefail, "cmd | grep -q" puede fallar
# por SIGPIPE en cmd aunque el texto sí aparezca.
jaeger_traces_contain() {
  local out
  out="$(curl -fsS --get "http://localhost:16686/api/v3/traces" \
    --data-urlencode "query.serviceName=$1" \
    --data-urlencode "query.startTimeMin=$(date -u -d '-1 hour' +%Y-%m-%dT%H:%M:%SZ)" \
    --data-urlencode "query.startTimeMax=$(date -u -d '+5 minutes' +%Y-%m-%dT%H:%M:%SZ)" \
    --data-urlencode "query.searchDepth=50")" || return 1
  grep -q -- "$2" <<<"$out"
}
collector_log_contains() {
  local out
  out="$(docker logs "$1" 2>&1)" || return 1
  grep -q -- "$2" <<<"$out"
}
http_ok() { curl -fsS "$1"; }

echo "== Lab 0 · entorno y prueba de humo"
labs/lab-env/up.sh
"$PY" labs/lab-env/smoke_test.py
wait_for "Jaeger recibió el servicio smoke-test" jaeger_has_service smoke-test
wait_for "Prometheus tiene smoke_runs_total" prom_has smoke_runs_total
wait_for "El Collector imprimió el log de la prueba" collector_log_contains otel-collector "Prueba de humo"

echo "== Labs 4 y 5 · trazas distribuidas y métricas"
(cd labs/lab05-metricas && nohup "$PY" dice_server.py > /tmp/dice_server.log 2>&1 &)
wait_for "dice-server responde" http_ok "http://localhost:8080/rolldice"
(cd labs/lab04-trazas && LAB_PARTIDAS=5 "$PY" player.py)
wait_for "Jaeger tiene dice-player" jaeger_has_service dice-player
wait_for "Jaeger tiene dice-server" jaeger_has_service dice-server
for metric in dice_rolls_total dice_roll_duration_seconds_bucket dice_requests_active dice_roll_last dice_players_known otelcol_receiver_accepted_spans otelcol_exporter_sent_spans; do
  wait_for "Prometheus tiene $metric" prom_has "$metric"
done

echo "== Lab 8 · Collector propio (solución)"
labs/lab-env/use-collector-config.sh labs/lab08-collector/solucion.yaml
wait_for "health_check responde" http_ok "http://localhost:13133/"
(cd labs/lab04-trazas && LAB_PARTIDAS=3 "$PY" player.py)
wait_for "Las trazas traen deployment.environment.name" jaeger_traces_contain dice-player "deployment.environment.name"

echo "== Lab 9 · agent → gateway con OTTL y span_metrics"
labs/lab-env/use-collector-config.sh labs/lab09-ottl-gateway/gateway.yaml gateway
labs/lab-env/use-collector-config.sh labs/lab09-ottl-gateway/agent.yaml
wait_for "health_check del agent responde" http_ok "http://localhost:13133/"
(cd labs/lab04-trazas && LAB_PARTIDAS=5 "$PY" player.py)
wait_for "Las trazas traen lab.sesion (OTTL)" jaeger_traces_contain dice-player "lab.sesion"
wait_for "Las trazas traen lab.collector.agent (agent)" jaeger_traces_contain dice-player "lab.collector.agent"
wait_for "Prometheus tiene traces_span_metrics_calls_total (connector)" prom_has traces_span_metrics_calls_total

echo "== Lab 11 · escenarios de depuración"
if labs/lab-env/use-collector-config.sh labs/lab11-depuracion/escenario-a.yaml; then
  echo "  FALLA  escenario-a.yaml debería ser rechazado por validate"; exit 1
fi
echo "  OK     escenario-a.yaml fue rechazado por validate"
labs/lab-env/use-collector-config.sh labs/lab11-depuracion/escenario-b.yaml
labs/lab-env/use-collector-config.sh labs/lab11-depuracion/escenario-b-solucion.yaml
wait_for "health_check responde con la solución del escenario B" http_ok "http://localhost:13133/"

echo "== Limpieza"
pkill -f "dice_server.py" || true
labs/lab-env/reset-collector.sh
labs/lab-env/down.sh
echo "E2E de laboratorios: OK"
