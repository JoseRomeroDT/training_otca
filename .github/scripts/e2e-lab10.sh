#!/usr/bin/env bash
# Prueba de extremo a extremo del Laboratorio 10 (kind + cert-manager + OpenTelemetry Operator).
# La ejecuta el CI y también sirve en un Codespace de 4 núcleos: bash .github/scripts/e2e-lab10.sh
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
L=labs/lab10-kubernetes

$L/cluster-up.sh
kubectl apply -f $L/collector.yaml
kubectl apply -f $L/instrumentation.yaml

echo "== Esperando el Deployment demo-collector creado por el Operator"
for _ in $(seq 1 60); do kubectl get deploy/demo-collector -n otca >/dev/null 2>&1 && break; sleep 3; done
kubectl rollout status deploy/demo-collector -n otca --timeout=300s

echo "== Imagen de la app"
docker build -t dice-app:lab10 $L/app
kind load docker-image dice-app:lab10 --name otca
kubectl apply -f $L/app.yaml
kubectl rollout status deploy/dice-app -n otca --timeout=300s

echo "== ¿Se inyectó la auto-instrumentación?"
# Salidas a archivo antes de buscar: con pipefail, "cmd | grep -q" puede fallar por SIGPIPE.
kubectl describe pod -n otca -l app=dice-app > /tmp/pod.txt
grep -q "opentelemetry-auto-instrumentation" /tmp/pod.txt
echo "  OK     init container de auto-instrumentación presente"

echo "== Tráfico"
kubectl port-forward -n otca svc/dice-app 8080:8080 >/tmp/pf.log 2>&1 &
PF=$!
for _ in $(seq 1 30); do curl -fsS "localhost:8080/health" >/dev/null 2>&1 && break; sleep 2; done
for _ in $(seq 1 10); do curl -fsS "localhost:8080/rolldice?player=ci" >/dev/null; done

echo "== ¿Llegaron los spans al Collector?"
ok=""
for _ in $(seq 1 30); do
  kubectl logs -n otca deploy/demo-collector > /tmp/collector.log 2>/dev/null || true
  if grep -q "GET /rolldice" /tmp/collector.log; then ok=1; break; fi
  sleep 3
done
kill "$PF" 2>/dev/null || true
if [ -z "$ok" ]; then
  echo "  FALLA  no hay spans GET /rolldice en el Collector"
  tail -60 /tmp/collector.log
  kubectl logs -n otca deploy/dice-app --all-containers > /tmp/app.log 2>&1 || true
  tail -60 /tmp/app.log
  cat /tmp/pod.txt
  exit 1
fi
echo "  OK     spans GET /rolldice en el Collector"
grep -m1 "service.name" /tmp/collector.log || true
grep -q "service.name: Str(dice-app)" /tmp/collector.log
echo "  OK     service.name derivado del Deployment (dice-app)"

$L/cluster-down.sh
echo "E2E del Laboratorio 10: OK"
