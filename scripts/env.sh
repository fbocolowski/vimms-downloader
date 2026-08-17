#!/usr/bin/env bash
# Shared bootstrap. ROOT must be set.

set -euo pipefail

: "${ROOT:?ROOT must be set}"

PYTHON="${PYTHON:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"

bootstrap_env() {
  cd "$ROOT"

  if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "Python not found: ${PYTHON}" >&2
    return 1
  fi

  if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating ${VENV_DIR}..."
    "$PYTHON" -m venv "$VENV_DIR"
  fi

  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"

  python -m pip install -q -r requirements.txt
  mkdir -p out
}
