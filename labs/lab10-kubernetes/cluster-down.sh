#!/usr/bin/env bash
# Lab 10 · Elimina el clúster kind "otca" (libera CPU y memoria del Codespace).
set -euo pipefail
kind delete cluster --name otca
