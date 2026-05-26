"""Pipeline tests with mocked DRC runner."""

from pathlib import Path
from unittest.mock import patch

import klayout.db as db
import klayout.rdb as rdb

from klayrb.config import DrcCheckConfig
from klayrb.pipeline import run_check

REPO_ROOT = Path(__file__).resolve().parents[1]


def _build_minimal_lyrdb(path: Path) -> None:
    database = rdb.ReportDatabase("mock")
    category = database.create_category("MOCK")
    cell = database.create_cell("TOP")
    item = database.create_item(cell.rdb_id(), category.rdb_id())
    item.add_value(db.DBox(0, 0, 0.5, 0.5))
    database.save(str(path))


@patch("klayrb.marker.browser.run_drc_batch")
def test_run_check_mocked_drc(mock_run, tmp_path):
    gds = tmp_path / "layout.gds"
    lyrdb = tmp_path / "layout.lyrdb"
    marked = tmp_path / "layout_annotated.gds"
    layer_map = tmp_path / "layout_annotated_layer_map.csv"

    layout = db.Layout()
    top = layout.create_cell("TOP")
    layout.layer(1, 0)
    layout.write(str(gds))

    def fake_drc(**kwargs):
        _build_minimal_lyrdb(lyrdb)
        return lyrdb

    mock_run.side_effect = fake_drc

    config = DrcCheckConfig(
        gds_path=gds,
        lydrc_path=REPO_ROOT / "Chipx_TFLN_DRC_QCI-V16-20240415.lydrc",
        lyrdb_path=lyrdb,
        marked_gds_path=marked,
        layer_map_path=layer_map,
        annotate_mode="layer_map",
    )
    result = run_check(config)

    assert result.lyrdb_path == lyrdb
    assert result.violation_count == 1
    assert marked.is_file()
    assert layer_map.is_file()
    assert result.layer_map_result is not None
    assert result.layer_map_result.markers_written == 1
    mock_run.assert_called_once()
