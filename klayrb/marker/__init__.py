"""Marker Browser (.lyrdb) and GDS marking."""

from klayrb.marker.annotate import (
    AnnotateGdsResult,
    annotate_gds_with_drc_errors,
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

__all__ = [
    "annotate_gds_with_drc_errors",
    "AnnotateGdsResult",
    "DEFAULT_MARKER_LAYER",
    "DEFAULT_LABEL_LAYER",
    "CategoryStats",
    "MarkerBrowserResult",
    "MarkerBrowserGenerator",
    "generate_lyrdb",
    "load_report_database",
    "summarize_report_database",
    "MarkerApplyResult",
    "apply_markers_to_layout",
]
