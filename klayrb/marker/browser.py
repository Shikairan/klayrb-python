"""Marker Browser (.lyrdb) generation and summary."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

import klayout.rdb as rdb

from klayrb.config import DrcCheckConfig
from klayrb.drc.runner import run_drc_batch


@dataclass
class CategoryStats:
    """Violation counts for one RDB category."""

    category_id: int
    name: str
    description: str
    count: int
    waived_count: int = 0


@dataclass
class MarkerBrowserResult:
    """Result of DRC / Marker Browser file generation."""

    lyrdb_path: Path
    violation_count: int
    waived_count: int
    categories: Dict[str, CategoryStats] = field(default_factory=dict)
    rdb: Optional[rdb.ReportDatabase] = None

    def summary_lines(self) -> list[str]:
        lines = [
            f"lyrdb: {self.lyrdb_path}",
            f"violations: {self.violation_count} (waived: {self.waived_count})",
        ]
        for stats in sorted(self.categories.values(), key=lambda s: s.name):
            lines.append(f"  {stats.name}: {stats.count}")
        return lines


def load_report_database(lyrdb_path: Path) -> rdb.ReportDatabase:
    path = Path(lyrdb_path)
    if not path.is_file():
        raise FileNotFoundError(f"lyrdb not found: {path}")
    database = rdb.ReportDatabase()
    database.load(str(path))
    return database


def summarize_report_database(database: rdb.ReportDatabase) -> MarkerBrowserResult:
    """Build statistics from an existing report database."""
    categories: Dict[str, CategoryStats] = {}
    category_counts: Dict[int, int] = {}
    category_waived: Dict[int, int] = {}
    waived_tag = _waived_tag_id(database)

    for item in database.each_item():
        cid = item.category_id()
        category_counts[cid] = category_counts.get(cid, 0) + 1
        if waived_tag and item.has_tag(waived_tag):
            category_waived[cid] = category_waived.get(cid, 0) + 1

    for cat in database.each_category():
        cid = cat.rdb_id()
        name = cat.path() or cat.name() or str(cid)
        categories[name] = CategoryStats(
            category_id=cid,
            name=name,
            description=(cat.description or "") if hasattr(cat, "description") else "",
            count=category_counts.get(cid, 0),
            waived_count=category_waived.get(cid, 0),
        )

    total = sum(category_counts.values())
    waived_total = sum(category_waived.values())

    return MarkerBrowserResult(
        lyrdb_path=Path(database.filename() or ""),
        violation_count=total,
        waived_count=waived_total,
        categories=categories,
        rdb=database,
    )


def _waived_tag_id(database: rdb.ReportDatabase) -> int:
    try:
        return database.tag_id("waived")
    except Exception:
        return 0


class MarkerBrowserGenerator:
    """Run DRC and produce / inspect Marker Browser (.lyrdb) files."""

    def __init__(self, config: DrcCheckConfig) -> None:
        self._config = config

    def generate(self) -> MarkerBrowserResult:
        """Run batch DRC and return loaded report database summary."""
        cfg = self._config
        assert cfg.lyrdb_path is not None
        run_drc_batch(
            gds_path=cfg.gds_path,
            lydrc_path=cfg.lydrc_path,
            lyrdb_path=cfg.lyrdb_path,
            klayout_path=cfg.klayout_path,
            timeout_s=cfg.drc_timeout_s,
        )
        return self.load_existing(cfg.lyrdb_path)

    def load_existing(self, lyrdb_path: Optional[Path] = None) -> MarkerBrowserResult:
        path = Path(lyrdb_path or self._config.lyrdb_path)
        database = load_report_database(path)
        result = summarize_report_database(database)
        result.lyrdb_path = path
        return result


def generate_lyrdb(config: DrcCheckConfig) -> MarkerBrowserResult:
    """Convenience: run DRC and return Marker Browser summary."""
    return MarkerBrowserGenerator(config).generate()
