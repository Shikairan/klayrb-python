"""Marker Browser (.lyrdb) and GDS marking."""

from klayrb.marker.annotate import (
    AnnotateGdsResult,
    AnnotateLayerMapResult,
    annotate_gds_with_drc_errors,
    annotate_gds_with_layer_map,
    DEFAULT_LABEL_LAYER,
    DEFAULT_MARKER_LAYER,
)
from klayrb.marker.applicator import MarkerApplyResult, apply_markers_to_layout
from klayrb.marker.browser import (
    CategoryStats,
    MarkerBrowserGenerator,
    MarkerBrowserResult,
    generate_lyrdb,
    load_report_database,
    summarize_report_database,
)
from klayrb.marker.category_layers import LayerMapEntry, build_category_layers
from klayrb.marker.layer_map_io import (
    default_layer_map_path,
    read_layer_map,
    write_layer_map_csv,
)

__all__ = [
    "annotate_gds_with_drc_errors",
    "annotate_gds_with_layer_map",
    "AnnotateGdsResult",
    "AnnotateLayerMapResult",
    "DEFAULT_MARKER_LAYER",
    "DEFAULT_LABEL_LAYER",
    "LayerMapEntry",
    "build_category_layers",
    "default_layer_map_path",
    "read_layer_map",
    "write_layer_map_csv",
    "CategoryStats",
    "MarkerBrowserResult",
    "MarkerBrowserGenerator",
    "generate_lyrdb",
    "load_report_database",
    "summarize_report_database",
    "MarkerApplyResult",
    "apply_markers_to_layout",
]
