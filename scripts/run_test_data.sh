#!/bin/bash
# Script to run the test data creation inside the container environment

set -o errexit
set -o nounset
set -o pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
COMPOSE_CMD=${COMPOSE_CMD:-$("$SCRIPT_DIR"/detect-compose.sh)}

if [[ -z "$COMPOSE_CMD" ]]; then
  echo "Unable to locate a compatible compose command. Set COMPOSE_CMD or install Docker/Podman." >&2
  exit 1
fi

# shellcheck disable=SC2206   # intentional word splitting into array
COMPOSE_ARGS=($COMPOSE_CMD)

echo "Running test data creation script inside container environment..."

"${COMPOSE_ARGS[@]}" -f docker-compose.dev.yml cp scripts/create_test_data.py backend:/tmp/create_test_data.py
"${COMPOSE_ARGS[@]}" -f docker-compose.dev.yml exec -w /app backend python3 /tmp/create_test_data.py

echo "Test data script execution completed!"
