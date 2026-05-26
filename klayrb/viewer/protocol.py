"""Layout view adapter protocol (GUI integration placeholder)."""

from __future__ import annotations

from typing import Any, Optional, Protocol, runtime_checkable

import klayout.rdb as rdb


@runtime_checkable
class ILayoutViewAdapter(Protocol):
    """
  Reserved interface for KLayout GUI / PyQt integration.

  A future implementation may use ``pya.LayoutView.current()`` inside the
  KLayout application process. This package does not call that API.
  """

    def is_available(self) -> bool:
        """Return True when a live layout view can be used."""
        ...

    def get_layout_view(self) -> Optional[Any]:
        """Return the underlying view object, or None."""
        ...

    def load_layout(self, gds_path: str) -> None:
        """Load a layout file into the view."""
        ...

    def load_marker_database(self, lyrdb_path: str) -> None:
        """Attach a Marker Browser report database to the view."""
        ...

    def highlight_from_rdb(self, database: rdb.ReportDatabase) -> None:
        """Display markers from an in-memory report database."""
        ...
