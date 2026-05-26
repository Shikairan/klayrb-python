"""Load DRC DSL from KLayout .lydrc macro files."""

from __future__ import annotations

import html
import xml.etree.ElementTree as ET
from pathlib import Path


class LydrcLoadError(Exception):
    """Raised when a .lydrc file cannot be parsed or validated."""


def load_dsl_from_lydrc(lydrc_path: Path) -> str:
    """
    Parse a KLayout .lydrc macro XML file and return the embedded DRC DSL text.

    Parameters
    ----------
    lydrc_path:
        Path to the .lydrc file.

    Returns
    -------
    str
        DRC DSL source (Ruby-based DRC language).

    Raises
    ------
    LydrcLoadError
        If the file is missing, not XML, or not a DRC DSL macro.
    """
    path = Path(lydrc_path)
    if not path.is_file():
        raise LydrcLoadError(f"lydrc file not found: {path}")

    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        raise LydrcLoadError(f"invalid XML in {path}: {exc}") from exc

    root = tree.getroot()
    if root.tag != "klayout-macro":
        raise LydrcLoadError(f"expected klayout-macro root in {path}")

    interpreter = _text_of(root, "interpreter")
    if interpreter and interpreter != "dsl":
        raise LydrcLoadError(
            f"unsupported interpreter {interpreter!r} in {path} (expected 'dsl')"
        )

    dsl_name = _text_of(root, "dsl-interpreter-name")
    if dsl_name and dsl_name != "drc-dsl-xml":
        raise LydrcLoadError(
            f"unsupported dsl-interpreter-name {dsl_name!r} in {path}"
        )

    text_elem = root.find("text")
    if text_elem is None or not (text_elem.text or "").strip():
        raise LydrcLoadError(f"empty or missing <text> in {path}")

    # ElementTree decodes standard entities; unescape any remaining HTML entities.
    return html.unescape(text_elem.text)


def _text_of(root: ET.Element, tag: str) -> str | None:
    elem = root.find(tag)
    if elem is None or elem.text is None:
        return None
    return elem.text.strip()
