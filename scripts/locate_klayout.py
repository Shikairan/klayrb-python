#!/usr/bin/env python3
"""Print KLayout executable search results (for troubleshooting PATH issues)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from klayrb.drc.runner import find_klayout_executable, iter_klayout_search_paths


def main() -> int:
    print("KLayout 查找路径（按优先级）:\n")
    for path in iter_klayout_search_paths():
        ok = path.is_file()
        mark = "OK" if ok else "-"
        print(f"  [{mark}] {path}")
    print()
    try:
        exe = find_klayout_executable()
        print(f"将使用: {exe}")
        return 0
    except Exception as exc:
        print(f"未找到: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
