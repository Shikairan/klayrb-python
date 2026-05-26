"""End-to-end DRC check pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from klayrb.config import DrcCheckConfig
from klayrb.marker.annotate import (
    AnnotateGdsResult,
    AnnotateLayerMapResult,
    annotate_gds_with_drc_errors,
    annotate_gds_with_layer_map,
)
from klayrb.marker.applicator import MarkerApplyResult, apply_markers_to_layout
from klayrb.marker.browser import MarkerBrowserGenerator, MarkerBrowserResult
from klayrb.viewer.noop import NoopLayoutViewAdapter, default_view_adapter
from klayrb.viewer.protocol import ILayoutViewAdapter


@dataclass
class DrcCheckResult:
    """Full pipeline result: Marker Browser file + optional marked GDS."""

    marker_result: MarkerBrowserResult
    marked_gds_path: Optional[Path] = None
    layer_map_path: Optional[Path] = None
    apply_result: Optional[MarkerApplyResult] = None
    annotate_result: Optional[AnnotateGdsResult] = None
    layer_map_result: Optional[AnnotateLayerMapResult] = None
    warnings: List[str] = field(default_factory=list)

    @property
    def lyrdb_path(self) -> Path:
        return self.marker_result.lyrdb_path

    @property
    def violation_count(self) -> int:
        return self.marker_result.violation_count

    @property
    def categories(self):
        return self.marker_result.categories


def run_check(
    config: DrcCheckConfig,
    view_adapter: Optional[ILayoutViewAdapter] = None,
) -> DrcCheckResult:
    """
    Run DRC (optional), summarize .lyrdb, apply markers to GDS, optional GUI hook.

    Parameters
    ----------
    config:
        Input paths and options.
    view_adapter:
        Optional layout view integration. Defaults to no-op (no GUI).
    """
    adapter = view_adapter if view_adapter is not None else default_view_adapter()
    generator = MarkerBrowserGenerator(config)
    warnings: List[str] = []

    if config.run_drc:
        marker_result = generator.generate()
    else:
        assert config.lyrdb_path is not None
        marker_result = generator.load_existing(config.lyrdb_path)

    marked_path: Optional[Path] = None
    layer_map_path: Optional[Path] = None
    apply_result: Optional[MarkerApplyResult] = None
    annotate_result: Optional[AnnotateGdsResult] = None
    layer_map_result: Optional[AnnotateLayerMapResult] = None

    if config.apply_markers:
        marked_path = config.resolve_marked_gds_path()
        assert config.lyrdb_path is not None
        mode = config.annotate_mode

        if mode == "layer_map":
            layer_map_path = config.resolve_layer_map_path()
            layer_map_result = annotate_gds_with_layer_map(
                str(config.gds_path),
                str(marker_result.lyrdb_path),
                str(marked_path),
                layer_map_path=str(layer_map_path),
                error_layer_base=config.error_layer_base,
                marker_datatype=config.marker_datatype,
                marker_size_um=config.marker_size_um,
                dbu_um=config.annotate_dbu_um,
            )
            warnings.extend(layer_map_result.warnings)
        elif mode == "legacy":
            annotate_result = annotate_gds_with_drc_errors(
                str(config.gds_path),
                str(marker_result.lyrdb_path),
                str(marked_path),
                marker_layer=config.marker_layer,
                label_layer=config.label_layer,
                marker_size_um=config.marker_size_um,
                dbu_um=config.annotate_dbu_um,
            )
            warnings.extend(annotate_result.warnings)
        else:
            apply_result = apply_markers_to_layout(
                gds_path=config.gds_path,
                lyrdb_path=marker_result.lyrdb_path,
                output_gds_path=marked_path,
                error_layer_base=config.error_layer_base,
            )
            warnings.extend(apply_result.warnings)

    if adapter.is_available() and marker_result.rdb is not None:
        adapter.load_layout(str(config.gds_path))
        adapter.load_marker_database(str(marker_result.lyrdb_path))
        adapter.highlight_from_rdb(marker_result.rdb)

    return DrcCheckResult(
        marker_result=marker_result,
        marked_gds_path=marked_path,
        layer_map_path=layer_map_path,
        apply_result=apply_result,
        annotate_result=annotate_result,
        layer_map_result=layer_map_result,
        warnings=warnings,
    )
