#!/usr/bin/env bash
set -euo pipefail

# Defaults match the Dockerfile args
: "${UID:=1000}"
: "${GID:=1000}"
: "${USER:=webapp}"

# Ensure storage structure exists
mkdir -p /storage/app /storage/logs

if [ "$(id -u)" = "0" ]; then
  # Take ownership of bind mounts (if possible) then set cooperative perms
  chown -R "${UID}:${GID}" /storage || true
  chmod -R ug+rwX /storage || true
  chmod g+s /storage /storage/app /storage/logs || true

  # Drop privileges to webapp and run
  exec gosu "${UID}:${GID}" uvicorn app.main:app --host "${UVICORN_HOST:-0.0.0.0}" --port "${UVICORN_PORT:-8000}"
else
  # Already non-root (e.g., user overridden in Compose) — just run
  exec uvicorn app.main:app --host "${UVICORN_HOST:-0.0.0.0}" --port "${UVICORN_PORT:-8000}"
fi
