#!/usr/bin/env python3
"""
Chipx TFLN DRC demo: Chipx_TFLN_DRC_QCI-V16-20240415.lydrc + P1 sample GDS.

Run from repository root::

    PYTHONPATH=. python3 demo/chipx_p1_demo.py

Outputs under ``demo/output/`` by default:

- ``P1_chipx.lyrdb`` — Marker Browser
- ``P1_chipx_annotated.gds`` — 按规则分 layer 方框标注（10000+）
- ``P1_chipx_annotated_layer_map.txt`` — layer ↔ 规则说明
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LYDRC = REPO_ROOT / "Chipx_TFLN_DRC_QCI-V16-20240415.lydrc"
DEFAULT_GDS = (
    REPO_ROOT
    / "tests/chipx_tfln/data/P1-20240625-SYD-LN600E300[17X15]-ITLA-V1.5.gds"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "demo/output"


def _print_banner() -> None:
    print("=" * 60)
    print("  klayrb Chipx TFLN DRC Demo")
    print("  Rules : Chipx_TFLN_DRC_QCI-V16-20240415.lydrc")
    print("  Layout: P1-20240625-SYD-LN600E300[17X15]-ITLA-V1.5.gds")
    print("=" * 60)
    print()


def _run_preview(gds_path: Path, lydrc_path: Path) -> int:
    import klayout.db as db

    from klayrb.drc.lydrc_loader import load_dsl_from_lydrc

    layout = db.Layout()
    layout.read(str(gds_path))
    print("--- 版图预览 ---")
    print(f"DBU (µm): {layout.dbu}")
    print(f"顶层 cell 数: {layout.cells()}")
    print(f"层数: {layout.layers()}")
    top = layout.top_cell()
    if top:
        print(f"Top cell: {top.name}")
    print()

    dsl = load_dsl_from_lydrc(lydrc_path)
    outputs = [
        line.strip()
        for line in dsl.splitlines()
        if ".output(" in line
    ]
    print(f"--- DRC 规则（共 {len(outputs)} 条 output）---")
    for line in outputs[:8]:
        print(f"  {line[:70]}")
    if len(outputs) > 8:
        print(f"  ... 另有 {len(outputs) - 8} 条")
    print()
    print("--- 运行完整 Demo ---")
    print("  PYTHONPATH=. python3 demo/chipx_p1_demo.py")
    return 0


def _print_summary(result) -> None:
    print("--- DRC 结果摘要 ---")
    print(f"Marker Browser (.lyrdb): {result.lyrdb_path}")
    print(f"违规总数: {result.violation_count}")
    if result.marker_result.waived_count:
        print(f"已 waive: {result.marker_result.waived_count}")

    if result.categories:
        print()
        print(f"{'类别':<50} {'数量':>8}")
        print("-" * 60)
        for stats in sorted(result.categories.values(), key=lambda s: -s.count):
            name = stats.name[:48]
            print(f"{name:<50} {stats.count:>8}")

    if result.marked_gds_path:
        print()
        print(f"输出 GDS: {result.marked_gds_path}")
        if result.layer_map_result:
            lr = result.layer_map_result
            print(f"Layer 对照表: {result.layer_map_path or lr.layer_map_path}")
            print(f"  DRC 层数: {len(lr.entries)} (layer 10000+)")
            print(f"  方框数: {lr.markers_written}")
            if lr.items_skipped:
                print(f"  跳过项: {lr.items_skipped}")
        elif result.annotate_result:
            ar = result.annotate_result
            print("标注模式: legacy 999/0 + 999/1 文本")
            print(f"  方框数: {ar.markers_written}")
            print(f"  文本数: {ar.labels_written}")
        elif result.apply_result:
            print(f"标注模式: geometry (完整违规几何)")
            print(f"  图形数: {result.apply_result.shapes_written}")
        if result.warnings:
            print(f"警告数: {len(result.warnings)}")


def _resolve_annotate_mode(args: argparse.Namespace) -> str:
    if getattr(args, "legacy_annotate", False):
        return "legacy"
    if args.category_layers:
        return "geometry"
    return getattr(args, "annotate_mode", "layer_map")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chipx + P1 GDS DRC demo")
    parser.add_argument("--lydrc", type=Path, default=DEFAULT_LYDRC)
    parser.add_argument("--gds", type=Path, default=DEFAULT_GDS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--klayout-path", type=Path, default=None)
    parser.add_argument(
        "--timeout",
        type=float,
        default=900.0,
        help="DRC subprocess timeout (seconds)",
    )
    parser.add_argument(
        "--no-mark-gds",
        action="store_true",
        help="Only generate .lyrdb",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Only inspect GDS/lydrc (no DRC)",
    )
    parser.add_argument(
        "--lyrdb",
        type=Path,
        default=None,
        help="Use existing .lyrdb (skip DRC)",
    )
    parser.add_argument(
        "--annotate-mode",
        choices=("layer_map", "legacy", "geometry"),
        default="layer_map",
        help="GDS marking mode (default: layer_map)",
    )
    parser.add_argument(
        "--category-layers",
        action="store_true",
        help="Same as --annotate-mode geometry",
    )
    parser.add_argument(
        "--legacy-annotate",
        action="store_true",
        help="Same as --annotate-mode legacy (999/0 + 999/1 text)",
    )
    parser.add_argument(
        "--marker-size-um",
        type=float,
        default=2.0,
        help="Marker box half-size in microns",
    )
    parser.add_argument(
        "--annotate-only",
        action="store_true",
        help="Only annotate from --lyrdb (skip DRC)",
    )
    args = parser.parse_args(argv)

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    from klayrb.config import DrcCheckConfig
    from klayrb.drc.runner import find_klayout_executable
    from klayrb.pipeline import run_check

    _print_banner()

    if not args.lydrc.is_file():
        print(f"error: lydrc not found: {args.lydrc}", file=sys.stderr)
        return 1
    if not args.gds.is_file():
        print(f"error: GDS not found: {args.gds}", file=sys.stderr)
        return 1

    annotate_mode = _resolve_annotate_mode(args)
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    lyrdb_path = args.lyrdb if args.lyrdb else out / "P1_chipx.lyrdb"
    marked_path = out / (
        "P1_chipx_marked.gds" if annotate_mode == "geometry" else "P1_chipx_annotated.gds"
    )
    layer_map_path = out / "P1_chipx_annotated_layer_map.txt"

    print(f"输入 GDS : {args.gds}")
    print(f"规则文件 : {args.lydrc}")
    print(f"输出目录 : {out}")
    print(f"标注模式 : {annotate_mode}")
    print()

    if args.preview:
        return _run_preview(args.gds, args.lydrc)

    if args.annotate_only:
        if args.lyrdb is None or not args.lyrdb.is_file():
            print("error: --annotate-only 需要已有 --lyrdb 文件", file=sys.stderr)
            return 1
        return _run_annotate_only(args, lyrdb_path, marked_path, layer_map_path, annotate_mode)

    run_drc = args.lyrdb is None
    if run_drc:
        try:
            klayout = find_klayout_executable(args.klayout_path)
            print(f"KLayout: {klayout}")
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            print(
                "请安装 KLayout 并确保 `klayout` 在 PATH，或使用 --klayout-path",
                file=sys.stderr,
            )
            print("也可先运行: python3 demo/chipx_p1_demo.py --preview", file=sys.stderr)
            return 1
        print("正在运行 DRC（可能需要数分钟）...")
        print()

    config = DrcCheckConfig(
        gds_path=args.gds,
        lydrc_path=args.lydrc,
        lyrdb_path=lyrdb_path,
        marked_gds_path=None if args.no_mark_gds else marked_path,
        layer_map_path=None if args.no_mark_gds else layer_map_path,
        klayout_path=args.klayout_path,
        drc_timeout_s=args.timeout,
        apply_markers=not args.no_mark_gds,
        run_drc=run_drc,
        annotate_mode=annotate_mode,
        marker_size_um=args.marker_size_um,
    )

    try:
        result = run_check(config)
    except Exception as exc:
        print(f"error: DRC failed: {exc}", file=sys.stderr)
        return 1

    _print_summary(result)
    print("在 KLayout GUI 中打开:")
    print(f"  klayout {args.gds} -m {result.lyrdb_path}")
    if result.marked_gds_path:
        print(f"  klayout {result.marked_gds_path}")
    if result.layer_map_path:
        print(f"Layer 对照: {result.layer_map_path}")

    return 0 if result.violation_count == 0 else 2


def _run_annotate_only(
    args: argparse.Namespace,
    lyrdb_path: Path,
    gds_out: Path,
    layer_map_path: Path,
    annotate_mode: str,
) -> int:
    from klayrb.marker.annotate import (
        annotate_gds_with_drc_errors,
        annotate_gds_with_layer_map,
    )
    from klayrb.marker.browser import load_report_database, summarize_report_database

    print("仅标注（跳过 DRC）")
    print(f"  .lyrdb : {lyrdb_path}")
    print(f"  模式   : {annotate_mode}")
    print()

    try:
        if annotate_mode == "layer_map":
            ann = annotate_gds_with_layer_map(
                str(args.gds),
                str(lyrdb_path),
                str(gds_out),
                layer_map_path=str(layer_map_path),
                marker_size_um=args.marker_size_um,
            )
            print("--- 标注完成 (layer_map) ---")
            print(f"方框数: {ann.markers_written}")
            print(f"DRC 层数: {len(ann.entries)}")
            print(f"对照表: {ann.layer_map_path}")
        elif annotate_mode == "legacy":
            ann = annotate_gds_with_drc_errors(
                str(args.gds),
                str(lyrdb_path),
                str(gds_out),
                marker_size_um=args.marker_size_um,
            )
            print("--- 标注完成 (legacy) ---")
            print(f"方框: {ann.markers_written}, 文本: {ann.labels_written}")
        else:
            from klayrb.marker.applicator import apply_markers_to_layout

            apply_markers_to_layout(
                gds_path=Path(args.gds),
                lyrdb_path=lyrdb_path,
                output_gds_path=gds_out,
            )
            print("--- 标注完成 (geometry) ---")
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    summary = summarize_report_database(load_report_database(lyrdb_path))
    print(f"违规总数 (.lyrdb): {summary.violation_count}")
    print(f"klayout {gds_out}")
    return 0 if summary.violation_count == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
