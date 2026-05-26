# Chipx TFLN + P1 样例 Demo

对仓库内 **Chipx DRC 规则** 与 **P1 样例 GDS** 跑完整流程：

1. KLayout 批处理 DRC → `demo/output/P1_chipx.lyrdb`（Marker Browser）
2. **硬标注** → `demo/output/P1_chipx_annotated.gds`
   - **999/0**：违规位置方框（默认半边长 2 µm）
   - **999/1**：规则名文本（如 `LD_FC_COR_S`）

## 输入文件

| 类型 | 路径 |
|------|------|
| 规则 | [`Chipx_TFLN_DRC_QCI-V16-20240415.lydrc`](../Chipx_TFLN_DRC_QCI-V16-20240415.lydrc) |
| 版图 | [`tests/chipx_tfln/data/P1-20240625-SYD-LN600E300[17X15]-ITLA-V1.5.gds`](../tests/chipx_tfln/data/P1-20240625-SYD-LN600E300[17X15]-ITLA-V1.5.gds) |

## 环境

```bash
pip install -r requirements.txt
```

**KLayout 可执行文件**（与 `pip install klayout` 的 Python 绑定不同）必须单独安装。

```bash
PYTHONPATH=. python3 scripts/locate_klayout.py
export KLAYRB_KLAYOUT=/path/to/klayout   # 若未在 PATH
```

## 运行

**预览**（无需 KLayout）：

```bash
PYTHONPATH=. python3 demo/chipx_p1_demo.py --preview
```

**完整 Demo**（DRC + 硬标注，默认）：

```bash
./demo/run_demo.sh
# 或
PYTHONPATH=. python3 demo/chipx_p1_demo.py
```

**仅有 .lyrdb 时，只做硬标注**：

```bash
PYTHONPATH=. python3 demo/chipx_p1_demo.py \
  --annotate-only \
  --lyrdb demo/output/P1_chipx.lyrdb
```

## 可选参数

| 参数 | 说明 |
|------|------|
| `--no-mark-gds` | 只生成 `.lyrdb` |
| `--lyrdb PATH` | 跳过 DRC，使用已有报告 |
| `--annotate-only` | 仅硬标注（必须配合 `--lyrdb`） |
| `--category-layers` | 改用 layer 10000+ 分类几何（非默认硬标注） |
| `--marker-size-um 2.0` | 方框半边长（µm） |
| `--klayout-path` | KLayout 可执行文件路径 |

## 查看结果

Marker Browser + 原版图：

```bash
klayout tests/chipx_tfln/data/P1-20240625-SYD-LN600E300[17X15]-ITLA-V1.5.gds \
  -m demo/output/P1_chipx.lyrdb
```

硬标注 GDS（999/0、999/1）：

```bash
klayout demo/output/P1_chipx_annotated.gds
```

## Python API（与 Demo 相同逻辑）

```python
from klayrb import annotate_gds_with_drc_errors

annotate_gds_with_drc_errors(
    "tests/chipx_tfln/data/P1-20240625-SYD-LN600E300[17X15]-ITLA-V1.5.gds",
    "demo/output/P1_chipx.lyrdb",
    "demo/output/P1_chipx_annotated.gds",
    marker_layer=(999, 0),
    label_layer=(999, 1),
    marker_size_um=2.0,
    dbu_um=0.001,
)
```

## 输出目录

`demo/output/` 已 `.gitignore`，不提交生成的 `.lyrdb` / `*_annotated.gds`。
