"""Map RDB categories to GDS layers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import klayout.db as db
import klayout.rdb as rdb


@dataclass
class LayerMapEntry:
    """One GDS layer assigned to an RDB violation category."""

    gds_layer: int
    datatype: int
    category_id: int
    rule_id: str
    description: str
    layout_layer_index: int = -1


@dataclass
class CategoryLayerBuildResult:
    """Category id -> layout layer index, plus legend entries."""

    category_to_layer_index: Dict[int, int]
    entries: List[LayerMapEntry]


def category_rule_id(category: rdb.RdbCategory) -> str:
    """Short rule id (text before colon in category name)."""
    name = (category.name() or category.path() or "").strip().strip("'\"")
    if not name:
        return f"DRC_{category.rdb_id()}"
    if ":" in name:
        name = name.split(":", 1)[0].strip()
    if len(name) > 64:
        name = name[:61] + "..."
    return name


def category_description(category: rdb.RdbCategory) -> str:
    """Human-readable description from RDB category."""
    text = (category.description or "").strip()
    if text:
        return text
    name = (category.name() or category.path() or "").strip().strip("'\"")
    return name or f"category {category.rdb_id()}"


def build_category_layers(
    layout: db.Layout,
    database: rdb.ReportDatabase,
    *,
    error_layer_base: int = 10000,
    marker_datatype: int = 0,
    layer_name_prefix: str = "DRC_ERR",
) -> CategoryLayerBuildResult:
    """
    Assign each RDB category a distinct GDS layer and register it on ``layout``.

    Returns mapping ``category_rdb_id -> layout_layer_index`` and legend entries.
    """
    category_to_layer_index: Dict[int, int] = {}
    entries: List[LayerMapEntry] = []

    categories = list(database.each_category())
    categories.sort(key=lambda c: c.rdb_id())

    for index, category in enumerate(categories):
        cid = category.rdb_id()
        gds_layer = error_layer_base + index
        rule_id = category_rule_id(category)
        description = category_description(category)

        layer_info = db.LayerInfo(gds_layer, marker_datatype)
        layer_info.name = f"{layer_name_prefix}_{rule_id}"

        layer_index = layout.layer(layer_info)
        category_to_layer_index[cid] = layer_index

        entries.append(
            LayerMapEntry(
                gds_layer=gds_layer,
                datatype=marker_datatype,
                category_id=cid,
                rule_id=rule_id,
                description=description,
                layout_layer_index=layer_index,
            )
        )

    return CategoryLayerBuildResult(
        category_to_layer_index=category_to_layer_index,
        entries=entries,
    )
