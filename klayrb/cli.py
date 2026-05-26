"""Command-line interface for klayrb."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from klayrb.config import DrcCheckConfig
from klayrb.pipeline import run_check


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="klayrb",
        description="GDS DRC check using KLayout .lydrc rules (python-klayout)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Run DRC and optionally mark violations on GDS")
    check.add_argument("--lydrc", required=True, type=Path, help="Path to .lydrc rule file")
    check.add_argument("--gds", required=True, type=Path, help="Input GDS layout")
    check.add_argument(
        "--lyrdb",
        type=Path,
        default=None,
        help="Output Marker Browser .lyrdb (default: <gds>.lyrdb)",
    )
    check.add_argument(
        "--marked-gds",
        type=Path,
        default=None,
        help="Output GDS with error layers (default: <gds>_marked.gds)",
    )
    check.add_argument(
        "--klayout-path",
        type=Path,
        default=None,
        help="Path to klayout executable",
    )
    check.add_argument(
        "--no-mark-gds",
        action="store_true",
        help="Only generate .lyrdb, do not write marked GDS",
    )
    check.add_argument(
        "--hard-annotate",
        action="store_true",
        help="Use fixed layers 999/0 boxes and 999/1 labels (annotate_gds_with_drc_errors)",
    )
    check.add_argument(
        "--marker-size-um",
        type=float,
        default=2.0,
        help="Half-size of hard-annotate marker box in microns",
    )
    check.add_argument(
        "--lyrdb-only",
        action="store_true",
        help="Skip DRC run; use existing --lyrdb and only mark GDS",
    )
    check.add_argument(
        "--error-layer-base",
        type=int,
        default=10000,
        help="Base GDS layer number for DRC error categories",
    )
    check.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="DRC subprocess timeout in seconds",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "check":
        return _cmd_check(args)
    parser.error(f"unknown command: {args.command}")
    return 2


def _cmd_check(args: argparse.Namespace) -> int:
    config = DrcCheckConfig(
        gds_path=args.gds,
        lydrc_path=args.lydrc,
        lyrdb_path=args.lyrdb,
        marked_gds_path=args.marked_gds,
        klayout_path=args.klayout_path,
        drc_timeout_s=args.timeout,
        error_layer_base=args.error_layer_base,
        apply_markers=not args.no_mark_gds,
        run_drc=not args.lyrdb_only,
        hard_annotate=args.hard_annotate,
        marker_size_um=args.marker_size_um,
    )

    try:
        result = run_check(config)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for line in result.marker_result.summary_lines():
        print(line)

    if result.marked_gds_path:
        print(f"marked_gds: {result.marked_gds_path}")
        if result.apply_result:
            print(f"marker_shapes: {result.apply_result.shapes_written}")

    for warning in result.warnings[:20]:
        print(f"warning: {warning}", file=sys.stderr)
    if len(result.warnings) > 20:
        print(f"... and {len(result.warnings) - 20} more warnings", file=sys.stderr)

    return 0 if result.violation_count == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
