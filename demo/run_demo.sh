#!/usr/bin/env bash
# Chipx + P1 DRC demo launcher (run from anywhere).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"
exec python3 "${ROOT}/demo/chipx_p1_demo.py" "$@"
