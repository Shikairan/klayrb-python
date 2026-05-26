"""Tests for KLayout executable discovery."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from klayrb.drc.runner import find_klayout_executable, iter_klayout_search_paths


def test_explicit_path(tmp_path):
    fake = tmp_path / "klayout"
    fake.write_text("#!/bin/sh\necho klayout\n")
    fake.chmod(0o755)
    assert find_klayout_executable(fake) == fake.resolve()


def test_env_klayrb_klayout(tmp_path, monkeypatch):
    fake = tmp_path / "my_klayout"
    fake.write_text("#!/bin/sh\ntrue\n")
    fake.chmod(0o755)
    monkeypatch.setenv("KLAYRB_KLAYOUT", str(fake))
    assert find_klayout_executable() == fake.resolve()


def test_not_found(monkeypatch):
    monkeypatch.delenv("KLAYRB_KLAYOUT", raising=False)
    with patch("klayrb.drc.runner.shutil.which", return_value=None):
        with patch(
            "klayrb.drc.runner._candidate_klayout_paths",
            return_value=[Path("/nonexistent/klayout_test_xyz")],
        ):
            with pytest.raises(Exception, match="klayout executable not found"):
                find_klayout_executable()
