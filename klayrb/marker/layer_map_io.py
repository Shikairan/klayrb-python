"""Read/write layer ↔ DRC category mapping as CSV."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from klayrb.marker.category_layers import LayerMapEntry

CSV_COLUMNS = ("layer", "datatype", "rule_id", "error")


def default_layer_map_path(gds_out: Path) -> Path:
    return gds_out.with_name(gds_out.stem + "_layer_map.csv")


def write_layer_map_csv(path: Path, entries: List[LayerMapEntry]) -> Path:
    """Write CSV with only the layer ↔ error mapping table (no comments)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(CSV_COLUMNS)
        for entry in entries:
            writer.writerow(
                [
                    entry.gds_layer,
                    entry.datatype,
                    entry.rule_id,
                    entry.description,
                ]
            )
    return path


def read_layer_map(path: Path) -> List[LayerMapEntry]:
    """Parse a layer map CSV written by ``write_layer_map_csv``."""
    path = Path(path)
    entries: List[LayerMapEntry] = []

    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            return entries
        for row in reader:
            layer_key = "layer" if "layer" in row else "gds_layer"
            error_key = "error" if "error" in row else "description"
            if layer_key not in row:
                continue
            entries.append(
                LayerMapEntry(
                    gds_layer=int(row[layer_key]),
                    datatype=int(row.get("datatype", 0)),
                    category_id=int(row.get("category_id", 0)),
                    rule_id=row.get("rule_id", ""),
                    description=row.get(error_key, ""),
                )
            )
    return entries


# Backward-compatible alias
write_layer_map_txt = write_layer_map_csv
