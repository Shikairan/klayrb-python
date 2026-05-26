"""Convert RDB marker geometries (micron, D-types) to layout database shapes."""

from __future__ import annotations

from typing import Iterator, List, Union

import klayout.db as db
import klayout.rdb as rdb

Insertable = Union[db.Box, db.Polygon, db.Edge, db.Path]
ShapeList = List[Insertable]


def um_to_dbu(value_um: float, dbu_um: float) -> int:
    """Convert microns to integer database units."""
    if dbu_um <= 0:
        raise ValueError(f"layout dbu must be positive, got {dbu_um}")
    return int(round(value_um / dbu_um))


def dbox_to_box(box: db.DBox, dbu_um: float) -> db.Box:
    return db.Box(
        um_to_dbu(box.left, dbu_um),
        um_to_dbu(box.bottom, dbu_um),
        um_to_dbu(box.right, dbu_um),
        um_to_dbu(box.top, dbu_um),
    )


def dpolygon_to_polygon(poly: db.DPolygon, dbu_um: float) -> db.Polygon:
    points = [
        db.Point(um_to_dbu(p.x, dbu_um), um_to_dbu(p.y, dbu_um))
        for p in poly.each_point_hull()
    ]
    return db.Polygon(points)


def dedge_to_edge(edge: db.DEdge, dbu_um: float) -> db.Edge:
    return db.Edge(
        um_to_dbu(edge.p1.x, dbu_um),
        um_to_dbu(edge.p1.y, dbu_um),
        um_to_dbu(edge.p2.x, dbu_um),
        um_to_dbu(edge.p2.y, dbu_um),
    )


def dedge_pair_to_shapes(edge_pair: db.DEdgePair, dbu_um: float) -> ShapeList:
    """Represent an edge pair as two edges (KLayout DRC marker style)."""
    return [
        dedge_to_edge(edge_pair.first, dbu_um),
        dedge_to_edge(edge_pair.second, dbu_um),
    ]


def dpath_to_path(path: db.DPath, dbu_um: float) -> db.Path:
    width_dbu = max(1, um_to_dbu(path.width, dbu_um))
    points = [
        db.Point(um_to_dbu(p.x, dbu_um), um_to_dbu(p.y, dbu_um))
        for p in path.each_point()
    ]
    return db.Path(points, width_dbu)


def value_to_shapes(value: rdb.RdbItemValue, dbu_um: float) -> ShapeList:
    """Map one RDB value object to zero or more layout shapes."""
    if value.is_polygon():
        return [dpolygon_to_polygon(value.polygon(), dbu_um)]
    if value.is_box():
        return [dbox_to_box(value.box(), dbu_um)]
    if value.is_edge():
        return [dedge_to_edge(value.edge(), dbu_um)]
    if value.is_edge_pair():
        return dedge_pair_to_shapes(value.edge_pair(), dbu_um)
    if value.is_path():
        return [dpath_to_path(value.path(), dbu_um)]
    return []


def iter_item_shapes(item: rdb.RdbItem, dbu_um: float) -> Iterator[Insertable]:
    for value in item.each_value():
        for shape in value_to_shapes(value, dbu_um):
            yield shape
