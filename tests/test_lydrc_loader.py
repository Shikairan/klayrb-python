"""Tests for .lydrc loading and batch script generation."""

from pathlib import Path

import pytest

from klayrb.drc.batch_script import build_batch_drc_script
from klayrb.drc.lydrc_loader import load_dsl_from_lydrc

REPO_ROOT = Path(__file__).resolve().parents[1]
CHIPX_LYDRC = REPO_ROOT / "Chipx_TFLN_DRC_QCI-V16-20240415.lydrc"


def test_load_chipx_lydrc():
    dsl = load_dsl_from_lydrc(CHIPX_LYDRC)
    assert "report(" in dsl
    assert "input(11, 0)" in dsl
    assert "LD_FC_COR_S" in dsl


def test_build_batch_script_injects_header():
    script = build_batch_drc_script(CHIPX_LYDRC)
    assert "if $input && $output" in script
    assert 'report("DRC report", $output)' in script
    assert script.count('report("DRC report")') == 1


def test_load_missing_file():
    with pytest.raises(Exception):
        load_dsl_from_lydrc(REPO_ROOT / "nonexistent.lydrc")
