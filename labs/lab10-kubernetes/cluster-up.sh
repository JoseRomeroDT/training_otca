#!/usr/bin/env bash
# Lab 10 · Crea el clúster kind "otca" e instala cert-manager y el OpenTelemetry
# Operator con versiones fijadas. Seguro de re-ejecutar.
#
# Fuentes:
#   https://kind.sigs.k8s.io/docs/user/quick-start/
#   https://cert-manager.io/docs/installation/kubectl/
#   https://opentelemetry.io/docs/platforms/kubernetes/operator/#getting-started
set -euo pipefail
CERT_MANAGER_VERSION="v1.21.3"
OPERATOR_VERSION="v0.163.0"
CLUSTER="otca"

echo "==> 1/4 Clúster kind '$CLUSTER'"
if kind get clusters 2>/dev/null | grep -qx "$CLUSTER"; then
  echo "    ya existe"
else
  kind create cluster --name "$CLUSTER"
fi
kubectl cluster-info --context "kind-$CLUSTER" >/dev/null

echo "==> 2/4 cert-manager $CERT_MANAGER_VERSION (lo necesita el webhook del Operator)"
kubectl apply -f "https://github.com/cert-manager/cert-manager/releases/download/${CERT_MANAGER_VERSION}/cert-manager.yaml"
kubectl wait --for=condition=Available deployment --all -n cert-manager --timeout=300s

echo "==> 3/4 OpenTelemetry Operator $OPERATOR_VERSION"
# Recién instalado, el webhook de cert-manager puede tardar unos segundos en
# aceptar recursos: se reintenta.
for intento in 1 2 3 4 5 6; do
  if kubectl apply -f "https://github.com/open-telemetry/opentelemetry-operator/releases/download/${OPERATOR_VERSION}/opentelemetry-operator.yaml"; then
    break
  fi
  echo "    reintento $intento en 10 s…"
  sleep 10
done
kubectl wait --for=condition=Available deployment --all -n opentelemetry-operator-system --timeout=300s

echo "==> 4/4 Namespace del laboratorio: otca"
kubectl create namespace otca --dry-run=client -o yaml | kubectl apply -f -

echo ""
echo "Listo. Pods del Operator:"
kubectl get pods -n opentelemetry-operator-system
