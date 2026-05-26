"""Configuration for GDS DRC checks."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

AnnotateMode = Literal["layer_map", "legacy", "geometry"]


@dataclass
class DrcCheckConfig:
    """Parameters for a full DRC check pipeline."""

    gds_path: Path
    lydrc_path: Path
    lyrdb_path: Optional[Path] = None
    marked_gds_path: Optional[Path] = None
    layer_map_path: Optional[Path] = None
    klayout_path: Optional[Path] = None
    drc_timeout_s: Optional[float] = None
    error_layer_base: int = 10000
    apply_markers: bool = True
    run_drc: bool = True
    annotate_mode: AnnotateMode = "layer_map"
    # Deprecated: use annotate_mode="legacy" instead
    hard_annotate: bool = False
    marker_layer: tuple = (999, 0)
    label_layer: tuple = (999, 1)
    marker_size_um: float = 2.0
    annotate_dbu_um: float = 0.001
    marker_datatype: int = 0

    def __post_init__(self) -> None:
        self.gds_path = Path(self.gds_path)
        self.lydrc_path = Path(self.lydrc_path)
        if self.lyrdb_path is None:
            self.lyrdb_path = self.gds_path.with_suffix(".lyrdb")
        else:
            self.lyrdb_path = Path(self.lyrdb_path)
        if self.marked_gds_path is not None:
            self.marked_gds_path = Path(self.marked_gds_path)
        if self.layer_map_path is not None:
            self.layer_map_path = Path(self.layer_map_path)
        if self.klayout_path is not None:
            self.klayout_path = Path(self.klayout_path)
        elif os.environ.get("KLAYRB_KLAYOUT", "").strip():
            self.klayout_path = Path(os.environ["KLAYRB_KLAYOUT"].strip())
        self.annotate_mode = self._resolve_annotate_mode()

    def _resolve_annotate_mode(self) -> AnnotateMode:
        if self.hard_annotate:
            return "legacy"
        return self.annotate_mode

    def resolve_marked_gds_path(self) -> Path:
        if self.marked_gds_path is not None:
            return self.marked_gds_path
        stem = self.gds_path.stem + "_annotated"
        if self.annotate_mode == "geometry":
            stem = self.gds_path.stem + "_marked"
        return self.gds_path.with_name(stem + self.gds_path.suffix)

    def resolve_layer_map_path(self) -> Path:
        if self.layer_map_path is not None:
            return self.layer_map_path
        marked = self.resolve_marked_gds_path()
        return marked.with_name(marked.stem + "_layer_map.csv")
