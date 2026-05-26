"""Chipx + P1 test data and lydrc sanity checks (no klayout binary required)."""

from pathlib import Path

import pytest

from klayrb.drc.batch_script import build_batch_drc_script
from klayrb.drc.lydrc_loader import load_dsl_from_lydrc

from tests.chipx_tfln.conftest import (
    GDS_FILENAME,
    GDS_PATH,
    LYDRC_FILENAME,
    LYDRC_PATH,
    requires_chipx_assets,
)


@requires_chipx_assets
def test_chipx_lydrc_exists(chipx_lydrc_path: Path):
    assert chipx_lydrc_path == LYDRC_PATH
    assert chipx_lydrc_path.name == LYDRC_FILENAME


@requires_chipx_assets
def test_chipx_gds_exists(chipx_gds_path: Path):
    assert chipx_gds_path == GDS_PATH
    assert chipx_gds_path.name == GDS_FILENAME
    assert chipx_gds_path.stat().st_size > 100_000


@requires_chipx_assets
def test_chipx_lydrc_dsl_contains_rules(chipx_lydrc_path: Path):
    dsl = load_dsl_from_lydrc(chipx_lydrc_path)
    for token in ("LD_FC_COR_S", "M1_S", "report(", "input(11, 0)"):
        assert token in dsl


@requires_chipx_assets
def test_chipx_batch_script_builds(chipx_lydrc_path: Path):
    script = build_batch_drc_script(chipx_lydrc_path)
    assert "source($input)" in script
    assert "LD_FC_COR_S" in script


@requires_chipx_assets
def test_chipx_gds_readable(chipx_gds_path: Path):
    import klayout.db as db

    layout = db.Layout()
    layout.read(str(chipx_gds_path))
    assert layout.cells() > 0
    assert layout.layers() > 0
