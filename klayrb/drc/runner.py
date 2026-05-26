"""Run KLayout DRC in batch mode via subprocess."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable, List, Optional

from klayrb.drc.batch_script import write_batch_drc_script

# Override via env: export KLAYRB_KLAYOUT=/path/to/klayout
_ENV_KLAYOUT = "KLAYRB_KLAYOUT"
# KLayout's own convention on some installs
_ENV_KLAYOUT_ALT = "KLAYOUT_HOME"


class DrcRunnerError(Exception):
    """Raised when the KLayout batch DRC process fails."""


def _candidate_klayout_paths() -> List[Path]:
    """Well-known install locations (OS-specific)."""
    home = Path.home()
    system = platform.system()
    candidates: List[Path] = [
        Path("/usr/bin/klayout"),
        Path("/usr/local/bin/klayout"),
        Path("/opt/klayout/klayout"),
        home / "KLayout" / "klayout",
        home / ".local" / "bin" / "klayout",
    ]
    if system == "Darwin":
        candidates.extend(
            [
                Path("/Applications/KLayout.app/Contents/MacOS/klayout"),
                Path("/Applications/klayout.app/Contents/MacOS/klayout"),
                home / "Applications" / "KLayout.app" / "Contents/MacOS/klayout",
            ]
        )
    elif system == "Windows":
        candidates.extend(
            [
                Path(r"C:\Program Files\KLayout\klayout.exe"),
                Path(r"C:\Program Files (x86)\KLayout\klayout.exe"),
                home / "KLayout" / "klayout.exe",
            ]
        )
    return candidates


def _paths_from_env() -> List[Path]:
    paths: List[Path] = []
    for key in (_ENV_KLAYOUT, "KLAYOUT_PATH", "KLAYOUT"):
        value = os.environ.get(key, "").strip()
        if value:
            paths.append(Path(value))
    klayout_home = os.environ.get(_ENV_KLAYOUT_ALT, "").strip()
    if klayout_home:
        base = Path(klayout_home)
        paths.append(base / "klayout")
        paths.append(base / "klayout.exe")
    return paths


def iter_klayout_search_paths(
    klayout_path: Optional[Path] = None,
) -> Iterable[Path]:
    """Yield paths to probe, in priority order."""
    if klayout_path is not None:
        yield Path(klayout_path)
    for path in _paths_from_env():
        yield path
    found = shutil.which("klayout")
    if found:
        yield Path(found)
    for path in _candidate_klayout_paths():
        yield path


def find_klayout_executable(klayout_path: Optional[Path] = None) -> Path:
    """
    Resolve the KLayout binary for batch DRC.

    Resolution order: explicit argument → ``KLAYRB_KLAYOUT`` / ``KLAYOUT_PATH``
    → ``PATH`` → common install directories.
    """
    tried: List[str] = []
    for candidate in iter_klayout_search_paths(klayout_path):
        tried.append(str(candidate))
        if candidate.is_file():
            return candidate.resolve()
    hint = (
        "klayout executable not found.\n"
        "  1) Install KLayout: https://www.klayout.de/build.html\n"
        "  2) Or set: export KLAYRB_KLAYOUT=/full/path/to/klayout\n"
        "  3) Or pass: --klayout-path /full/path/to/klayout\n"
        f"  Searched: {', '.join(tried[:12])}"
        + (" ..." if len(tried) > 12 else "")
    )
    raise DrcRunnerError(hint)


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
