#!/usr/bin/env bash
# Extract out/*.zip|*.7z -> out/ (deletes archives; use --no-delete to keep)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/env.sh
source "${ROOT}/scripts/env.sh"

bootstrap_env
exec python -m scripts.extract "$@"
