"""
klayrb — GDS DRC checking with KLayout .lydrc rules (python-klayout).

Import API (no pip install required; add repo root to PYTHONPATH)::

    from klayrb import run_check, DrcCheckConfig
    from klayrb.marker import generate_lyrdb, apply_markers_to_layout
"""

from klayrb.config import DrcCheckConfig
from klayrb.pipeline import DrcCheckResult, run_check
from klayrb.marker import (
    MarkerBrowserResult,
    MarkerApplyResult,
    apply_markers_to_layout,
    generate_lyrdb,
)
from klayrb.drc import run_drc_batch, load_dsl_from_lydrc

__all__ = [
    "DrcCheckConfig",
    "DrcCheckResult",
    "run_check",
    "generate_lyrdb",
    "apply_markers_to_layout",
    "MarkerBrowserResult",
    "MarkerApplyResult",
    "run_drc_batch",
    "load_dsl_from_lydrc",
]

__version__ = "0.1.0"
