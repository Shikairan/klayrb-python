"""Tests for applying RDB markers to layout."""

from pathlib import Path

import klayout.db as db
import klayout.rdb as rdb

from klayrb.marker.applicator import apply_markers_to_layout

FIXTURES = Path(__file__).parent / "fixtures"


def _make_fixture_gds_and_lyrdb(tmp_path: Path) -> tuple[Path, Path]:
    gds_path = tmp_path / "test.gds"
    lyrdb_path = tmp_path / "test.lyrdb"

    layout = db.Layout()
    layout.dbu = 0.001
    top = layout.create_cell("TOP")
    l1 = layout.layer(1, 0)
    top.shapes(l1).insert(db.Box(0, 0, 1000, 1000))
    layout.write(str(gds_path))

    database = rdb.ReportDatabase("test")
    category = database.create_category("TEST_CAT")
    category.description = "test violation"

    cell = database.create_cell("TOP")
    item = database.create_item(cell.rdb_id(), category.rdb_id())  # noqa: RDB ids
    item.add_value(db.DBox(0.0, 0.0, 1.0, 1.0))

    database.save(str(lyrdb_path))
    return gds_path, lyrdb_path


def test_apply_markers(tmp_path):
    gds_path, lyrdb_path = _make_fixture_gds_and_lyrdb(tmp_path)
    out_path = tmp_path / "marked.gds"

    result = apply_markers_to_layout(
        gds_path=gds_path,
        lyrdb_path=lyrdb_path,
        output_gds_path=out_path,
        error_layer_base=10000,
    )

    assert out_path.is_file()
    assert result.shapes_written >= 1

    layout = db.Layout()
    layout.read(str(out_path))
    assert layout.layers() >= 2
