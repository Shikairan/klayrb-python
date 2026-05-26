"""Hard-annotate DRC violations on GDS (fixed marker / label layers)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

import klayout.db as db
import klayout.rdb as rdb

from klayrb.marker.browser import load_report_database
from klayrb.marker.category_layers import (
    LayerMapEntry,
    build_category_layers,
    category_rule_id,
)
from klayrb.marker.geometry import um_to_dbu
from klayrb.marker.layer_map_io import default_layer_map_path, write_layer_map_txt

# 默认硬编码标注层
DEFAULT_MARKER_LAYER: Tuple[int, int] = (999, 0)
DEFAULT_LABEL_LAYER: Tuple[int, int] = (999, 1)
DEFAULT_MARKER_SIZE_UM: float = 2.0
DEFAULT_DBU_UM: float = 0.001


@dataclass
class AnnotateGdsResult:
    """Statistics from annotate_gds_with_drc_errors."""

    gds_out: str
    markers_written: int
    labels_written: int
    items_skipped: int
    warnings: List[str] = field(default_factory=list)


def annotate_gds_with_drc_errors(
    gds_in: str,
    rdb_in: str,
    gds_out: str,
    marker_layer: tuple = DEFAULT_MARKER_LAYER,
    label_layer: tuple = DEFAULT_LABEL_LAYER,
    marker_size_um: float = DEFAULT_MARKER_SIZE_UM,
    dbu_um: float = DEFAULT_DBU_UM,
) -> AnnotateGdsResult:
    """
    在 GDS 上硬标注 DRC 错误，并保存到新的 GDS 文件。

    每个 RDB 违规项在 ``marker_layer`` 上绘制固定尺寸的方框标记，
    在 ``label_layer`` 上写入规则类别文本。

    Parameters
    ----------
    gds_in:
        输入 GDS 路径。
    rdb_in:
        KLayout 报告数据库路径（``.lyrdb``）。
    gds_out:
        输出 GDS 路径（保留原版图所有层，并追加标注层）。
    marker_layer:
        错误标记框 GDS 层号 ``(layer, datatype)``，默认 ``(999, 0)``。
    label_layer:
        规则名称文本层 ``(layer, datatype)``，默认 ``(999, 1)``。
    marker_size_um:
        标记方框半边长（微米）；以违规几何中心为圆心。
    dbu_um:
        数据库单位（微米/dbu），当读入的 layout 未设置 dbu 时使用；
        默认 ``0.001``（1 nm）。

    Returns
    -------
    AnnotateGdsResult
        写入统计与警告信息。
    """
    gds_in_path = Path(gds_in)
    rdb_in_path = Path(rdb_in)
    gds_out_path = Path(gds_out)

    if not gds_in_path.is_file():
        raise FileNotFoundError(f"gds_in not found: {gds_in}")
    if not rdb_in_path.is_file():
        raise FileNotFoundError(f"rdb_in not found: {rdb_in}")

    layout = db.Layout()
    layout.read(str(gds_in_path))

    effective_dbu = layout.dbu if layout.dbu and layout.dbu > 0 else dbu_um
    if effective_dbu <= 0:
        effective_dbu = DEFAULT_DBU_UM

    marker_li = db.LayerInfo(int(marker_layer[0]), int(marker_layer[1]))
    marker_li.name = "DRC_MARKER"
    label_li = db.LayerInfo(int(label_layer[0]), int(label_layer[1]))
    label_li.name = "DRC_LABEL"

    marker_layer_index = layout.layer(marker_li)
    label_layer_index = layout.layer(label_li)

    database = load_report_database(rdb_in_path)
    cell_by_name = {c.name: c for c in layout.each_cell()}

    half_dbu = um_to_dbu(marker_size_um, effective_dbu)
    text_height_dbu = max(half_dbu, um_to_dbu(0.5, effective_dbu))

    markers_written = 0
    labels_written = 0
    items_skipped = 0
    warnings: List[str] = []

    for item in database.each_item():
        rdb_cell = database.cell_by_id(item.cell_id())
        if rdb_cell is None:
            items_skipped += 1
            warnings.append(f"unknown rdb cell id {item.cell_id()}")
            continue

        layout_cell = cell_by_name.get(rdb_cell.name())
        if layout_cell is None:
            items_skipped += 1
            warnings.append(f"layout cell not found: {rdb_cell.name()!r}")
            continue

        anchor = _item_anchor_um(item)
        if anchor is None:
            items_skipped += 1
            warnings.append(f"no geometry for item in cell {rdb_cell.name()!r}")
            continue

        cx_um, cy_um = anchor
        cx = um_to_dbu(cx_um, effective_dbu)
        cy = um_to_dbu(cy_um, effective_dbu)

        marker_box = db.Box(cx - half_dbu, cy - half_dbu, cx + half_dbu, cy + half_dbu)
        layout_cell.shapes(marker_layer_index).insert(marker_box)
        markers_written += 1

        category = database.category_by_id(item.category_id())
        label = (
            category_rule_id(category)
            if category is not None
            else f"DRC_{item.category_id()}"
        )
        text = db.Text(
            label,
            db.Trans(db.Vector(cx, cy)),
        )
        text.size = text_height_dbu
        layout_cell.shapes(label_layer_index).insert(text)
        labels_written += 1

    gds_out_path.parent.mkdir(parents=True, exist_ok=True)
    layout.write(str(gds_out_path))

    return AnnotateGdsResult(
        gds_out=str(gds_out_path),
        markers_written=markers_written,
        labels_written=labels_written,
        items_skipped=items_skipped,
        warnings=warnings,
    )


@dataclass
class AnnotateLayerMapResult:
    """Statistics from annotate_gds_with_layer_map."""

    gds_out: str
    layer_map_path: str
    entries: List[LayerMapEntry]
    markers_written: int
    items_skipped: int
    warnings: List[str] = field(default_factory=list)


def annotate_gds_with_layer_map(
    gds_in: str,
    rdb_in: str,
    gds_out: str,
    layer_map_path: str | None = None,
    error_layer_base: int = 10000,
    marker_datatype: int = 0,
    marker_size_um: float = DEFAULT_MARKER_SIZE_UM,
    dbu_um: float = DEFAULT_DBU_UM,
) -> AnnotateLayerMapResult:
    """
    按 RDB 类别分 GDS layer 标注违规（方框 only），并写出 layer 对照 txt。

    同一 category 使用同一 ``(layer, datatype)``；不在 GDS 中写入 Text。
    """
    gds_in_path = Path(gds_in)
    rdb_in_path = Path(rdb_in)
    gds_out_path = Path(gds_out)

    if not gds_in_path.is_file():
        raise FileNotFoundError(f"gds_in not found: {gds_in}")
    if not rdb_in_path.is_file():
        raise FileNotFoundError(f"rdb_in not found: {rdb_in}")

    map_path = (
        Path(layer_map_path)
        if layer_map_path
        else default_layer_map_path(gds_out_path)
    )

    layout = db.Layout()
    layout.read(str(gds_in_path))

    effective_dbu = layout.dbu if layout.dbu and layout.dbu > 0 else dbu_um
    if effective_dbu <= 0:
        effective_dbu = DEFAULT_DBU_UM

    database = load_report_database(rdb_in_path)
    built = build_category_layers(
        layout,
        database,
        error_layer_base=error_layer_base,
        marker_datatype=marker_datatype,
    )
    category_layers = built.category_to_layer_index
    entries = built.entries

    write_layer_map_txt(
        map_path,
        entries,
        gds_path=gds_out_path,
        rdb_path=rdb_in_path,
    )

    cell_by_name = {c.name: c for c in layout.each_cell()}
    half_dbu = um_to_dbu(marker_size_um, effective_dbu)

    markers_written = 0
    items_skipped = 0
    warnings: List[str] = []

    for item in database.each_item():
        rdb_cell = database.cell_by_id(item.cell_id())
        if rdb_cell is None:
            items_skipped += 1
            warnings.append(f"unknown rdb cell id {item.cell_id()}")
            continue

        layout_cell = cell_by_name.get(rdb_cell.name())
        if layout_cell is None:
            items_skipped += 1
            warnings.append(f"layout cell not found: {rdb_cell.name()!r}")
            continue

        layer_index = category_layers.get(item.category_id())
        if layer_index is None:
            items_skipped += 1
            warnings.append(f"unknown category id {item.category_id()}")
            continue

        anchor = _item_anchor_um(item)
        if anchor is None:
            items_skipped += 1
            warnings.append(f"no geometry for item in cell {rdb_cell.name()!r}")
            continue

        cx_um, cy_um = anchor
        cx = um_to_dbu(cx_um, effective_dbu)
        cy = um_to_dbu(cy_um, effective_dbu)
        marker_box = db.Box(cx - half_dbu, cy - half_dbu, cx + half_dbu, cy + half_dbu)
        layout_cell.shapes(layer_index).insert(marker_box)
        markers_written += 1

    gds_out_path.parent.mkdir(parents=True, exist_ok=True)
    layout.write(str(gds_out_path))

    return AnnotateLayerMapResult(
        gds_out=str(gds_out_path),
        layer_map_path=str(map_path),
        entries=entries,
        markers_written=markers_written,
        items_skipped=items_skipped,
        warnings=warnings,
    )


def _item_anchor_um(item: rdb.RdbItem) -> Optional[Tuple[float, float]]:
    """Violation anchor in microns (average of value centroids)."""
    xs: List[float] = []
    ys: List[float] = []

    for value in item.each_value():
        center = _value_center_um(value)
        if center is not None:
            xs.append(center[0])
            ys.append(center[1])

    if not xs:
        return None
    return sum(xs) / len(xs), sum(ys) / len(ys)


def _value_center_um(value: rdb.RdbItemValue) -> Optional[Tuple[float, float]]:
    if value.is_box():
        b = value.box()
        return (b.left + b.right) * 0.5, (b.bottom + b.top) * 0.5
    if value.is_polygon():
        b = value.polygon().bbox()
        return (b.left + b.right) * 0.5, (b.bottom + b.top) * 0.5
    if value.is_edge():
        e = value.edge()
        return (e.p1.x + e.p2.x) * 0.5, (e.p1.y + e.p2.y) * 0.5
    if value.is_edge_pair():
        ep = value.edge_pair()
        m1x = (ep.first.p1.x + ep.first.p2.x) * 0.5
        m1y = (ep.first.p1.y + ep.first.p2.y) * 0.5
        m2x = (ep.second.p1.x + ep.second.p2.x) * 0.5
        m2y = (ep.second.p1.y + ep.second.p2.y) * 0.5
        return (m1x + m2x) * 0.5, (m1y + m2y) * 0.5
    if value.is_path():
        b = value.path().bbox()
        return (b.left + b.right) * 0.5, (b.bottom + b.top) * 0.5
    return None
