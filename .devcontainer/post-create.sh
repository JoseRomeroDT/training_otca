#!/usr/bin/env bash
# Prepara el Codespace del entrenamiento OTCA (se ejecuta una sola vez, al crearlo).
#  1. Crea el entorno Python de los laboratorios (.venv) con versiones fijadas.
#  2. Instala kind (Kubernetes in Docker) para el Lab 10, verificando su SHA256.
#  3. Descarga por adelantado las imágenes del entorno de laboratorio.
set -euo pipefail
cd "$(dirname "$0")/.."
WORKSPACE="$PWD"

echo "==> 1/3 Entorno Python de los laboratorios (.venv)"
python -m venv .venv
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r labs/requirements.txt
if ! grep -q "otca-venv" "$HOME/.bashrc"; then
  echo "source \"$WORKSPACE/.venv/bin/activate\"  # otca-venv" >> "$HOME/.bashrc"
fi

echo "==> 2/3 kind (Kubernetes in Docker) para el Lab 10"
KIND_VERSION="v0.33.0"
ARCH="$(dpkg --print-architecture)"   # amd64 o arm64
TMP="$(mktemp -d)"
(
  cd "$TMP"
  curl -fsSLO "https://github.com/kubernetes-sigs/kind/releases/download/${KIND_VERSION}/kind-linux-${ARCH}"
  curl -fsSLO "https://github.com/kubernetes-sigs/kind/releases/download/${KIND_VERSION}/kind-linux-${ARCH}.sha256sum"
  sha256sum -c "kind-linux-${ARCH}.sha256sum"
  sudo install -m 0755 "kind-linux-${ARCH}" /usr/local/bin/kind
)
rm -rf "$TMP"

echo "==> 3/3 Imágenes del entorno de laboratorio"
docker compose -f labs/lab-env/compose.yaml --profile gateway pull --quiet || \
  echo "Aviso: no se pudieron descargar las imágenes ahora; se descargarán con labs/lab-env/up.sh"

echo ""
echo "Codespace listo. Siguiente paso: abre una terminal nueva y ejecuta"
echo "  labs/lab-env/up.sh"
echo "Guía: Laboratorio 0 del sitio del entrenamiento."
