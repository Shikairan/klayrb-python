# klayrb-python

基于 [python-klayout](https://www.klayout.de/doc/programming/python.html) 的 GDS DRC 检查工具：读取已有 `.lydrc` 规则，对 GDS 执行 KLayout DRC，生成 Marker Browser 用的 `.lyrdb`，并将违规几何写入带错误层的 GDS。

## 依赖

- Python 3.9+
- `pip install -r requirements.txt`（安装 `klayout` Python 绑定）
- 系统安装 **KLayout 可执行文件**（用于批处理 DRC：`klayout -b -r ...`）

> **说明**：`pip install klayout` 是 Python API，**不能**替代 KLayout 应用程序；DRC 必须调用系统中的 `klayout` 程序。

### 安装 KLayout 并配置路径

下载：https://www.klayout.de/build.html

```bash
# 诊断：列出搜索路径及是否找到
PYTHONPATH=. python3 scripts/locate_klayout.py
```

已安装但报 `not found on PATH` 时：

```bash
export KLAYRB_KLAYOUT=/完整路径/klayout    # Linux / macOS
./demo/run_demo.sh --klayout-path /完整路径/klayout
```

Ubuntu `.deb` 示例（版本号以官网为准）：

```bash
wget https://www.klayout.org/downloads/Ubuntu-22/klayout_0.28.17-1_amd64.deb
sudo apt install ./klayout_0.28.17-1_amd64.deb
which klayout
```

## 使用方式（无需 pip 安装包）

将仓库根目录加入 `PYTHONPATH`，或在该目录下运行：

```bash
export PYTHONPATH=/path/to/klayrb-python:$PYTHONPATH
```

### 命令行

```bash
python -m klayrb check \
  --lydrc Chipx_TFLN_DRC_QCI-V16-20240415.lydrc \
  --gds layout.gds \
  --lyrdb layout.lyrdb \
  --marked-gds layout_marked.gds
```

常用选项：

| 选项 | 说明 |
|------|------|
| `--no-mark-gds` | 只生成 `.lyrdb`，不写标记 GDS |
| `--lyrdb-only` | 跳过 DRC，用已有 `.lyrdb` 写标记 GDS |
| `--klayout-path` | 指定 `klayout` 可执行文件路径 |
| `--error-layer-base` | 错误层起始 GDS layer 号（默认 10000） |

退出码：无违规为 0；存在违规为 2；运行错误为 1。

### Python API（供其他工具 import）

```python
from pathlib import Path
from klayrb import DrcCheckConfig, run_check
from klayrb.marker import generate_lyrdb, apply_markers_to_layout

# 完整流程：DRC → .lyrdb → 标记 GDS
result = run_check(DrcCheckConfig(
    gds_path=Path("layout.gds"),
    lydrc_path=Path("Chipx_TFLN_DRC_QCI-V16-20240415.lydrc"),
    lyrdb_path=Path("layout.lyrdb"),
    marked_gds_path=Path("layout_marked.gds"),
))
print(result.violation_count, result.categories)

# 按类别分 layer + txt 图例（默认，无 GDS 文本）
from klayrb import annotate_gds_with_layer_map
annotate_gds_with_layer_map(
    "layout.gds", "layout.lyrdb", "layout_annotated.gds",
    layer_map_path="layout_annotated_layer_map.csv",
)

# 分步调用
from klayrb.drc import run_drc_batch
run_drc_batch(
    gds_path=Path("layout.gds"),
    lydrc_path=Path("Chipx_TFLN_DRC_QCI-V16-20240415.lydrc"),
    lyrdb_path=Path("layout.lyrdb"),
)
```

### 在 KLayout GUI 中查看 Marker Browser

```bash
klayout layout.gds -m layout.lyrdb
```

## 架构

1. **lydrc_loader**：解析 `.lydrc` XML，提取 DRC DSL。
2. **batch_script**：注入 `source($input)` / `report(..., $output)` 批处理头。
3. **runner**：`klayout -b -r batch.drc -rd input=... -rd output=...`
4. **marker/browser**：加载 `.lyrdb`，统计违规类别（Marker Browser 文件由 KLayout DRC 原生生成）。
5. **marker/applicator**：将 RDB 几何写入 GDS 错误层（`10000+` 按类别递增）。
6. **viewer/protocol**：预留 `ILayoutViewAdapter`，默认 `NoopLayoutViewAdapter`（**不**实现 `pya.LayoutView.current()`）。

## 测试

```bash
pip install -r requirements.txt
PYTHONPATH=. pytest tests/ -q
```

### Chipx + P1 样例集成测试

专用目录 [`tests/chipx_tfln/`](tests/chipx_tfln/)，使用 `Chipx_TFLN_DRC_QCI-V16-20240415.lydrc` 与 `data/P1-20240625-SYD-LN600E300[17X15]-ITLA-V1.5.gds`：

```bash
PYTHONPATH=. python3 -m pytest tests/chipx_tfln/ -v
# 跳过需要 klayout 可执行文件的用例：
PYTHONPATH=. python3 -m pytest tests/chipx_tfln/ -v -m "not chipx_drc"
```

详见 [`tests/chipx_tfln/README.md`](tests/chipx_tfln/README.md)。

### Chipx + P1 Demo

一键演示（规则 + P1 GDS），**默认 layer_map**：每类违规一层 + `*_layer_map.csv`：

```bash
./demo/run_demo.sh
# 输出: demo/output/P1_chipx.lyrdb, P1_chipx_annotated.gds, P1_chipx_annotated_layer_map.csv
```

说明见 [`demo/README.md`](demo/README.md)。

## 仓库内 DRC 规则

- [`Chipx_TFLN_DRC_QCI-V16-20240415.lydrc`](Chipx_TFLN_DRC_QCI-V16-20240415.lydrc) — TuringQ LNOI 工艺 DRC 规则集
