"""Read/write layer ↔ DRC category mapping files."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from klayrb.marker.category_layers import LayerMapEntry

_HEADER_LINES = (
    "# klayrb layer map",
    "# generated_by: klayrb",
)
_COLUMN_HEADER = "layer\tdatatype\tcategory_id\trule_id\tdescription"


def default_layer_map_path(gds_out: Path) -> Path:
    return gds_out.with_name(gds_out.stem + "_layer_map.txt")


def write_layer_map_txt(
    path: Path,
    entries: List[LayerMapEntry],
    *,
    gds_path: Optional[Path] = None,
    rdb_path: Optional[Path] = None,
) -> Path:
    """Write TSV layer map with comment header."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = list(_HEADER_LINES)
    if gds_path is not None:
        lines.append(f"# gds: {gds_path}")
    if rdb_path is not None:
        lines.append(f"# rdb: {rdb_path}")
    lines.append(_COLUMN_HEADER)

    for entry in entries:
        desc = entry.description.replace("\t", " ").replace("\n", " ")
        lines.append(
            f"{entry.gds_layer}\t{entry.datatype}\t{entry.category_id}\t"
            f"{entry.rule_id}\t{desc}"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def read_layer_map(path: Path) -> List[LayerMapEntry]:
    """Parse a layer map file written by ``write_layer_map_txt``."""
    path = Path(path)
    entries: List[LayerMapEntry] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("layer\t"):
            continue
        parts = line.split("\t")
        if len(parts) < 5:
            continue
        entries.append(
            LayerMapEntry(
                gds_layer=int(parts[0]),
                datatype=int(parts[1]),
                category_id=int(parts[2]),
                rule_id=parts[3],
                description=parts[4],
            )
        )
    return entries
