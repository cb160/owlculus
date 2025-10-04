#!/usr/bin/env bash
# Utility script to locate a compatible compose command (Docker or Podman).

set -o errexit
set -o nounset
set -o pipefail

if [[ -n "${COMPOSE_CMD:-}" ]]; then
  echo "$COMPOSE_CMD"
  exit 0
fi

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  echo "docker compose"
  exit 0
fi

if command -v docker-compose >/dev/null 2>&1; then
  echo "docker-compose"
  exit 0
fi

if command -v podman >/dev/null 2>&1; then
  if podman compose version >/dev/null 2>&1; then
    echo "podman compose"
    exit 0
  fi
fi

if command -v podman-compose >/dev/null 2>&1; then
  echo "podman-compose"
  exit 0
fi

exit 1
