# Chipx TFLN + P1 样例 Demo

对仓库内 **Chipx DRC 规则** 与 **P1 样例 GDS** 跑完整流程：

1. KLayout 批处理 DRC → `demo/output/P1_chipx.lyrdb`（Marker Browser）
2. **按规则分 layer 硬标注** → `demo/output/P1_chipx_annotated.gds`
   - 每种 DRC 违规类别一个 GDS layer（默认从 **10000** 起）
   - 仅方框标记，**不写 GDS 文本**
3. **Layer 对照表** → `demo/output/P1_chipx_annotated_layer_map.txt`

## 输入文件

| 类型 | 路径 |
|------|------|
| 规则 | [`Chipx_TFLN_DRC_QCI-V16-20240415.lydrc`](../Chipx_TFLN_DRC_QCI-V16-20240415.lydrc) |
| 版图 | [`tests/chipx_tfln/data/P1-20240625-SYD-LN600E300[17X15]-ITLA-V1.5.gds`](../tests/chipx_tfln/data/P1-20240625-SYD-LN600E300[17X15]-ITLA-V1.5.gds) |

## 环境

```bash
pip install -r requirements.txt
PYTHONPATH=. python3 scripts/locate_klayout.py
export KLAYRB_KLAYOUT=/path/to/klayout   # 若需要
```

## 运行

```bash
./demo/run_demo.sh
# 或
PYTHONPATH=. python3 demo/chipx_p1_demo.py --preview   # 无需 KLayout
PYTHONPATH=. python3 demo/chipx_p1_demo.py             # 完整流程
```

## 标注模式

| 模式 | 参数 | 输出 |
|------|------|------|
| **layer_map**（默认） | — | `*_annotated.gds` + `*_layer_map.txt` |
| legacy | `--legacy-annotate` | 999/0 方框 + 999/1 文本 |
| geometry | `--category-layers` | 10000+ 完整违规几何 |

仅有 `.lyrdb` 时：

```bash
PYTHONPATH=. python3 demo/chipx_p1_demo.py \
  --annotate-only --lyrdb demo/output/P1_chipx.lyrdb
```

## Layer 对照表示例

```text
layer	datatype	category_id	rule_id	description
10000	0	1	LD_FC_COR_S	ld_fc_cor space < ...
10001	0	2	M1_S	M1 space < ...
```

在 KLayout 中打开 `P1_chipx_annotated.gds`，按 layer 开关显示，并对照 txt 查规则含义。

## Python API

```python
from klayrb import annotate_gds_with_layer_map

annotate_gds_with_layer_map(
    "tests/chipx_tfln/data/P1-....gds",
    "demo/output/P1_chipx.lyrdb",
    "demo/output/P1_chipx_annotated.gds",
    layer_map_path="demo/output/P1_chipx_annotated_layer_map.txt",
)
```
