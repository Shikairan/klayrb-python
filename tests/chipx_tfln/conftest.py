"""Shared fixtures for Chipx TFLN + P1 GDS integration tests."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

# tests/chipx_tfln/
CHIPX_TEST_DIR = Path(__file__).resolve().parent
REPO_ROOT = CHIPX_TEST_DIR.parents[1]

LYDRC_FILENAME = "Chipx_TFLN_DRC_QCI-V16-20240415.lydrc"
GDS_FILENAME = "P1-20240625-SYD-LN600E300[17X15]-ITLA-V1.5.gds"

LYDRC_PATH = REPO_ROOT / LYDRC_FILENAME
GDS_PATH = CHIPX_TEST_DIR / "data" / GDS_FILENAME

# Large layout DRC can take several minutes.
CHIPX_DRC_TIMEOUT_S = float(os.environ.get("KLAYRB_CHIPX_DRC_TIMEOUT", "900"))


def klayout_available() -> bool:
    return shutil.which("klayout") is not None


def chipx_assets_available() -> bool:
    return LYDRC_PATH.is_file() and GDS_PATH.is_file()


requires_chipx_assets = pytest.mark.skipif(
    not chipx_assets_available(),
    reason=f"missing {LYDRC_FILENAME} or {GDS_FILENAME} under tests/chipx_tfln/data/",
)

requires_klayout = pytest.mark.skipif(
    not klayout_available(),
    reason="klayout executable not found on PATH (required for batch DRC)",
)

chipx_drc = pytest.mark.chipx_drc


@pytest.fixture(scope="session")
def chipx_lydrc_path() -> Path:
    if not LYDRC_PATH.is_file():
        pytest.fail(f"lydrc not found: {LYDRC_PATH}")
    return LYDRC_PATH


@pytest.fixture(scope="session")
def chipx_gds_path() -> Path:
    if not GDS_PATH.is_file():
        pytest.fail(
            f"GDS not found: {GDS_PATH}\n"
            "Place the layout file in tests/chipx_tfln/data/ or clone from the repo."
        )
    return GDS_PATH


@pytest.fixture
def chipx_work_dir(tmp_path, request) -> Path:
    """Per-test working directory; optionally kept when KLAYRB_CHIPX_KEEP_OUTPUT=1."""
    work = tmp_path / "chipx_run"
    work.mkdir(parents=True, exist_ok=True)
    yield work
    if os.environ.get("KLAYRB_CHIPX_KEEP_OUTPUT"):
        keep_root = CHIPX_TEST_DIR / "output" / request.node.name
        keep_root.parent.mkdir(parents=True, exist_ok=True)
        if keep_root.exists():
            shutil.rmtree(keep_root)
        shutil.copytree(work, keep_root)
