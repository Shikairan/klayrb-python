"""Default no-op layout view adapter."""

from __future__ import annotations

from typing import Any, Optional

import klayout.rdb as rdb

from klayrb.viewer.protocol import ILayoutViewAdapter


class NoopLayoutViewAdapter:
    """Stub adapter: GUI highlighting is not available."""

    def is_available(self) -> bool:
        return False

    def get_layout_view(self) -> Optional[Any]:
        return None

    def load_layout(self, gds_path: str) -> None:
        pass

    def load_marker_database(self, lyrdb_path: str) -> None:
        pass

    def highlight_from_rdb(self, database: rdb.ReportDatabase) -> None:
        pass


def default_view_adapter() -> ILayoutViewAdapter:
    return NoopLayoutViewAdapter()
