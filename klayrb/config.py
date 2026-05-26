"""Configuration for GDS DRC checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class DrcCheckConfig:
    """Parameters for a full DRC check pipeline."""

    gds_path: Path
    lydrc_path: Path
    lyrdb_path: Optional[Path] = None
    marked_gds_path: Optional[Path] = None
    klayout_path: Optional[Path] = None
    drc_timeout_s: Optional[float] = None
    error_layer_base: int = 10000
    apply_markers: bool = True
    run_drc: bool = True

    def __post_init__(self) -> None:
        self.gds_path = Path(self.gds_path)
        self.lydrc_path = Path(self.lydrc_path)
        if self.lyrdb_path is None:
            self.lyrdb_path = self.gds_path.with_suffix(".lyrdb")
        else:
            self.lyrdb_path = Path(self.lyrdb_path)
        if self.marked_gds_path is not None:
            self.marked_gds_path = Path(self.marked_gds_path)
        if self.klayout_path is not None:
            self.klayout_path = Path(self.klayout_path)

    def resolve_marked_gds_path(self) -> Path:
        if self.marked_gds_path is not None:
            return self.marked_gds_path
        stem = self.gds_path.stem + "_marked"
        return self.gds_path.with_name(stem + self.gds_path.suffix)
