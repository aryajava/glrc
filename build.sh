#!/usr/bin/env bash
set -euo pipefail

PYTHON_EXE="python3"
if [[ -x ".venv/bin/python" ]]; then
    PYTHON_EXE=".venv/bin/python"
fi

LANG_TARGET="${1:-all}"

cmd=("${PYTHON_EXE}" "scripts/build.py" "--lang" "${LANG_TARGET}")
if [[ "${2:-}" == "refreshcache" ]]; then
    cmd+=("--refresh-icon-cache")
fi

"${cmd[@]}"
