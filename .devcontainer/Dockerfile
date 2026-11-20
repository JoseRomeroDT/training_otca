FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# El repositorio de Yarn preinstalado tiene la clave GPG caducada y rompe
# apt-get update (lo usan las features del devcontainer). Se elimina.
RUN rm -f /etc/apt/sources.list.d/yarn.list /etc/apt/trusted.gpg.d/yarn*.gpg \
 && apt-get update \
 && apt-get install -y --no-install-recommends jq \
 && rm -rf /var/lib/apt/lists/*
