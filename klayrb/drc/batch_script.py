"""Build batch-mode DRC scripts from .lydrc DSL."""

from __future__ import annotations

import re
from pathlib import Path

from klayrb.drc.lydrc_loader import load_dsl_from_lydrc

_BATCH_HEADER = """\
# injected by klayrb — batch mode
if $input && $output
  source($input)
  report("DRC report", $output)
else
  report("DRC report")
end

"""

# Standalone report line at script start (GUI mode default in many decks).
_REPORT_LINE_RE = re.compile(
    r'^\s*report\s*\(\s*["\']DRC report["\']\s*\)\s*$',
    re.MULTILINE,
)


def build_batch_drc_script(lydrc_path: Path) -> str:
    """
    Combine batch header with DSL from .lydrc, removing duplicate report() calls.
    """
    dsl = load_dsl_from_lydrc(lydrc_path)
    dsl = _REPORT_LINE_RE.sub("", dsl, count=1)
    return _BATCH_HEADER + dsl.lstrip("\n")


def write_batch_drc_script(lydrc_path: Path, output_path: Path) -> Path:
    """Write a temporary .drc file suitable for ``klayout -b -r``."""
    content = build_batch_drc_script(lydrc_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path
