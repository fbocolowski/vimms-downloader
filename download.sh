#!/usr/bin/env bash
# Download links.txt -> out/
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/env.sh
source "${ROOT}/scripts/env.sh"

if [[ ! -f "${ROOT}/links.txt" ]]; then
  echo "Missing links.txt" >&2
  exit 1
fi

bootstrap_env
exec python -m scripts.download
