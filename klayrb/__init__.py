"""
klayrb — GDS DRC checking with KLayout .lydrc rules (python-klayout).

Import API (no pip install required; add repo root to PYTHONPATH)::

    from klayrb import run_check, DrcCheckConfig
    from klayrb import annotate_gds_with_layer_map
"""

from klayrb.config import AnnotateMode, DrcCheckConfig
from klayrb.pipeline import DrcCheckResult, run_check
from klayrb.marker import (
    AnnotateGdsResult,
    AnnotateLayerMapResult,
    LayerMapEntry,
    MarkerBrowserResult,
    MarkerApplyResult,
    annotate_gds_with_drc_errors,
    annotate_gds_with_layer_map,
    apply_markers_to_layout,
    generate_lyrdb,
)
from klayrb.drc import run_drc_batch, load_dsl_from_lydrc

__all__ = [
    "DrcCheckConfig",
    "DrcCheckResult",
    "AnnotateMode",
    "run_check",
    "annotate_gds_with_layer_map",
    "annotate_gds_with_drc_errors",
    "AnnotateLayerMapResult",
    "AnnotateGdsResult",
    "LayerMapEntry",
    "generate_lyrdb",
    "apply_markers_to_layout",
    "MarkerBrowserResult",
    "MarkerApplyResult",
    "run_drc_batch",
    "load_dsl_from_lydrc",
]

__version__ = "0.1.0"
