"""Tests for annotate_gds_with_drc_errors."""

from pathlib import Path

import klayout.db as db
import klayout.rdb as rdb

from klayrb.marker.annotate import (
    DEFAULT_LABEL_LAYER,
    DEFAULT_MARKER_LAYER,
    annotate_gds_with_drc_errors,
)


def _make_gds_and_rdb(tmp_path: Path) -> tuple[str, str]:
    gds = tmp_path / "in.gds"
    lyrdb = tmp_path / "in.lyrdb"

    layout = db.Layout()
    layout.dbu = 0.001
    top = layout.create_cell("TOP")
    layout.layer(1, 0)
    layout.write(str(gds))

    database = rdb.ReportDatabase("test")
    category = database.create_category("LD_FC_COR_S: space violation")
    cell = database.create_cell("TOP")
    item = database.create_item(cell.rdb_id(), category.rdb_id())
    item.add_value(db.DBox(10.0, 20.0, 11.0, 21.0))
    database.save(str(lyrdb))
    return str(gds), str(lyrdb)


def test_annotate_hard_layers(tmp_path):
    gds_in, rdb_in = _make_gds_and_rdb(tmp_path)
    gds_out = str(tmp_path / "out.gds")

    result = annotate_gds_with_drc_errors(
        gds_in,
        rdb_in,
        gds_out,
        marker_layer=DEFAULT_MARKER_LAYER,
        label_layer=DEFAULT_LABEL_LAYER,
        marker_size_um=2.0,
        dbu_um=0.001,
    )

    assert result.markers_written == 1
    assert result.labels_written == 1
    assert Path(gds_out).is_file()

    layout = db.Layout()
    layout.read(gds_out)
    marker_idx = layout.find_layer(999, 0)
    label_idx = layout.find_layer(999, 1)
    assert marker_idx is not None
    assert label_idx is not None

    top = layout.cell("TOP")
    assert top.shapes(marker_idx).size() == 1
    assert top.shapes(label_idx).size() == 1


def test_annotate_label_shortens_rule_name(tmp_path):
    gds_in, rdb_in = _make_gds_and_rdb(tmp_path)
    gds_out = str(tmp_path / "out.gds")
    annotate_gds_with_drc_errors(gds_in, rdb_in, gds_out)

    layout = db.Layout()
    layout.read(gds_out)
    label_idx = layout.find_layer(999, 1)
    top = layout.cell("TOP")
    texts = []
    for shape in top.shapes(label_idx).each():
        if shape.is_text():
            texts.append(shape.text.string.strip("'\""))
    assert texts == ["LD_FC_COR_S"]
