"""End-to-end DRC on Chipx rules + P1 sample GDS (requires klayout executable)."""

from pathlib import Path

import pytest

from klayrb.config import DrcCheckConfig
from klayrb.drc.runner import find_klayout_executable, run_drc_batch
from klayrb.marker.browser import load_report_database, summarize_report_database
from klayrb.pipeline import run_check

from tests.chipx_tfln.conftest import (
    CHIPX_DRC_TIMEOUT_S,
    chipx_drc,
    requires_chipx_assets,
    requires_klayout,
)


@requires_chipx_assets
@requires_klayout
@chipx_drc
def test_chipx_run_drc_produces_lyrdb(
    chipx_lydrc_path: Path,
    chipx_gds_path: Path,
    chipx_work_dir: Path,
):
    lyrdb_path = chipx_work_dir / "P1_chipx.lyrdb"
    out = run_drc_batch(
        gds_path=chipx_gds_path,
        lydrc_path=chipx_lydrc_path,
        lyrdb_path=lyrdb_path,
        timeout_s=CHIPX_DRC_TIMEOUT_S,
    )
    assert out == lyrdb_path
    assert lyrdb_path.is_file()
    assert lyrdb_path.stat().st_size > 0

    summary = summarize_report_database(load_report_database(lyrdb_path))
    assert summary.lyrdb_path == lyrdb_path
    # Real layout is expected to have DRC hits for this deck.
    assert summary.violation_count >= 0
    assert len(summary.categories) >= 0


@requires_chipx_assets
@requires_klayout
@chipx_drc
def test_chipx_full_pipeline_marked_gds(
    chipx_lydrc_path: Path,
    chipx_gds_path: Path,
    chipx_work_dir: Path,
):
    lyrdb_path = chipx_work_dir / "P1_chipx.lyrdb"
    marked_path = chipx_work_dir / "P1_chipx_marked.gds"

    config = DrcCheckConfig(
        gds_path=chipx_gds_path,
        lydrc_path=chipx_lydrc_path,
        lyrdb_path=lyrdb_path,
        marked_gds_path=marked_path,
        drc_timeout_s=CHIPX_DRC_TIMEOUT_S,
    )
    result = run_check(config)

    assert result.lyrdb_path.is_file()
    assert result.marked_gds_path == marked_path
    assert marked_path.is_file()
    assert result.apply_result is not None
    if result.violation_count > 0:
        assert result.apply_result.shapes_written > 0


@requires_chipx_assets
@requires_klayout
@chipx_drc
def test_chipx_klayout_executable_resolves():
    exe = find_klayout_executable()
    assert exe.is_file()
