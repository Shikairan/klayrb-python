"""Configuration for GDS DRC checks."""

from __future__ import annotations

import os
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
    # 硬标注模式：固定 layer 999/0 方框 + 999/1 文本（见 annotate_gds_with_drc_errors）
    hard_annotate: bool = False
    marker_layer: tuple = (999, 0)
    label_layer: tuple = (999, 1)
    marker_size_um: float = 2.0
    annotate_dbu_um: float = 0.001

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
        elif os.environ.get("KLAYRB_KLAYOUT", "").strip():
            self.klayout_path = Path(os.environ["KLAYRB_KLAYOUT"].strip())

    def resolve_marked_gds_path(self) -> Path:
        if self.marked_gds_path is not None:
            return self.marked_gds_path
        stem = self.gds_path.stem + "_marked"
        return self.gds_path.with_name(stem + self.gds_path.suffix)
