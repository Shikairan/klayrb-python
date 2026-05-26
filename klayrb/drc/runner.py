"""Run KLayout DRC in batch mode via subprocess."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from klayrb.drc.batch_script import write_batch_drc_script


class DrcRunnerError(Exception):
    """Raised when the KLayout batch DRC process fails."""


def find_klayout_executable(klayout_path: Optional[Path] = None) -> Path:
    if klayout_path is not None:
        path = Path(klayout_path)
        if not path.is_file():
            raise DrcRunnerError(f"klayout executable not found: {path}")
        return path
    found = shutil.which("klayout")
    if not found:
        raise DrcRunnerError(
            "klayout executable not found on PATH; install KLayout or set klayout_path"
        )
    return Path(found)


def run_drc_batch(
    *,
    gds_path: Path,
    lydrc_path: Path,
    lyrdb_path: Path,
    klayout_path: Optional[Path] = None,
    timeout_s: Optional[float] = None,
) -> Path:
    """
    Execute DRC and write a Marker Browser (.lyrdb) report database.

    Uses ``klayout -b -r <script.drc> -rd input=... -rd output=...``.
    """
    gds_path = Path(gds_path).resolve()
    lydrc_path = Path(lydrc_path).resolve()
    lyrdb_path = Path(lyrdb_path).resolve()

    if not gds_path.is_file():
        raise DrcRunnerError(f"GDS file not found: {gds_path}")
    if not lydrc_path.is_file():
        raise DrcRunnerError(f"lydrc file not found: {lydrc_path}")

    klayout = find_klayout_executable(klayout_path)
    lyrdb_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="klayrb_drc_") as tmp:
        script_path = Path(tmp) / "batch.drc"
        write_batch_drc_script(lydrc_path, script_path)

        cmd = [
            str(klayout),
            "-b",
            "-r",
            str(script_path),
            "-rd",
            f"input={gds_path}",
            "-rd",
            f"output={lyrdb_path}",
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_s,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise DrcRunnerError(
                f"klayout DRC timed out after {timeout_s}s"
            ) from exc

        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            detail = stderr or stdout or f"exit code {result.returncode}"
            raise DrcRunnerError(f"klayout DRC failed: {detail}")

    if not lyrdb_path.is_file():
        raise DrcRunnerError(f"lyrdb was not created: {lyrdb_path}")

    return lyrdb_path
