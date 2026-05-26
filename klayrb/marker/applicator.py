"""Apply RDB markers onto a layout as error layers."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import klayout.db as db
import klayout.rdb as rdb

from klayrb.marker.browser import load_report_database
from klayrb.marker.category_layers import build_category_layers
from klayrb.marker.geometry import iter_item_shapes

logger = logging.getLogger(__name__)


@dataclass
class MarkerApplyResult:
    """Outcome of writing RDB markers into a layout."""

    output_gds_path: Path
    shapes_written: int
    items_skipped: int
    warnings: List[str] = field(default_factory=list)


def apply_markers_to_layout(
    *,
    gds_path: Path,
    lyrdb_path: Path,
    output_gds_path: Path,
    error_layer_base: int = 10000,
    layout: Optional[db.Layout] = None,
) -> MarkerApplyResult:
    """
    Load GDS, insert RDB violation geometries on per-category error layers, write GDS.
    """
    gds_path = Path(gds_path)
    lyrdb_path = Path(lyrdb_path)
    output_gds_path = Path(output_gds_path)

    own_layout = layout is None
    if layout is None:
        layout = db.Layout()
        layout.read(str(gds_path))

    database = load_report_database(lyrdb_path)
    dbu_um = layout.dbu

    built = build_category_layers(
        layout, database, error_layer_base=error_layer_base
    )
    category_layers = built.category_to_layer_index
    cell_by_name = {c.name: c for c in layout.each_cell()}

    shapes_written = 0
    items_skipped = 0
    warnings: List[str] = []

    for item in database.each_item():
        rdb_cell = database.cell_by_id(item.cell_id())
        if rdb_cell is None:
            items_skipped += 1
            warnings.append(f"unknown rdb cell id {item.cell_id()}")
            continue

        cell_name = rdb_cell.name()
        layout_cell = cell_by_name.get(cell_name)
        if layout_cell is None:
            items_skipped += 1
            warnings.append(f"layout cell not found: {cell_name!r}")
            continue

        layer_index = category_layers.get(item.category_id())
        if layer_index is None:
            items_skipped += 1
            continue

        target = layout_cell.shapes(layer_index)

        for shape in iter_item_shapes(item, dbu_um):
            target.insert(shape)
            shapes_written += 1

    output_gds_path.parent.mkdir(parents=True, exist_ok=True)
    layout.write(str(output_gds_path))

    if own_layout:
        # layout owned locally; nothing to detach
        pass

    return MarkerApplyResult(
        output_gds_path=output_gds_path,
        shapes_written=shapes_written,
        items_skipped=items_skipped,
        warnings=warnings,
    )
