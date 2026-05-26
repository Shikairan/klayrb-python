"""Tests for per-category layer map annotation."""

from pathlib import Path

import klayout.db as db
import klayout.rdb as rdb

from klayrb.marker.annotate import annotate_gds_with_layer_map
from klayrb.marker.layer_map_io import read_layer_map


def _make_two_category_rdb(tmp_path: Path) -> tuple[str, str]:
    gds = tmp_path / "in.gds"
    lyrdb = tmp_path / "in.lyrdb"

    layout = db.Layout()
    layout.dbu = 0.001
    layout.create_cell("TOP")
    layout.write(str(gds))

    database = rdb.ReportDatabase("test")
    cat_a = database.create_category("RULE_A: violation A")
    cat_a.description = "first rule"
    cat_b = database.create_category("RULE_B: violation B")
    cat_b.description = "second rule"
    cell = database.create_cell("TOP")
    item_a = database.create_item(cell.rdb_id(), cat_a.rdb_id())
    item_a.add_value(db.DBox(1.0, 2.0, 1.5, 2.5))
    item_b = database.create_item(cell.rdb_id(), cat_b.rdb_id())
    item_b.add_value(db.DBox(5.0, 6.0, 5.5, 6.5))
    database.save(str(lyrdb))
    return str(gds), str(lyrdb)


def test_layer_map_two_categories(tmp_path):
    gds_in, rdb_in = _make_two_category_rdb(tmp_path)
    gds_out = str(tmp_path / "out.gds")
    map_path = str(tmp_path / "out_layer_map.txt")

    result = annotate_gds_with_layer_map(
        gds_in,
        rdb_in,
        gds_out,
        layer_map_path=map_path,
        error_layer_base=10000,
    )

    assert result.markers_written == 2
    assert len(result.entries) == 2
    assert Path(gds_out).is_file()
    assert Path(map_path).is_file()

    layout = db.Layout()
    layout.read(gds_out)
    assert layout.find_layer(999, 0) is None
    assert layout.find_layer(999, 1) is None
    assert layout.find_layer(10000, 0) is not None
    assert layout.find_layer(10001, 0) is not None

    top = layout.cell("TOP")
    assert top.shapes(layout.find_layer(10000, 0)).size() == 1
    assert top.shapes(layout.find_layer(10001, 0)).size() == 1
    label_layer = layout.find_layer(10000, 1)
    if label_layer is not None:
        assert top.shapes(label_layer).size() == 0

    entries = read_layer_map(Path(map_path))
    assert len(entries) == 2
    rule_ids = {e.rule_id for e in entries}
    assert rule_ids == {"RULE_A", "RULE_B"}
    layers = {e.gds_layer for e in entries}
    assert layers == {10000, 10001}
