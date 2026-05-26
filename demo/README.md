# Chipx TFLN + P1 样例 Demo

对仓库内 **Chipx DRC 规则** 与 **P1 样例 GDS** 跑完整流程：

1. KLayout 批处理 DRC → `demo/output/P1_chipx.lyrdb`（Marker Browser）
2. 将违规写入错误层 → `demo/output/P1_chipx_marked.gds`

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
# 检查能否找到 klayout
PYTHONPATH=. python3 scripts/locate_klayout.py

# 若提示未找到，设置路径后运行 demo
export KLAYRB_KLAYOUT=/path/to/klayout
./demo/run_demo.sh
```

## 运行

**预览模式**（无需 KLayout，查看版图与规则条数）：

```bash
PYTHONPATH=. python3 demo/chipx_p1_demo.py --preview
```

**完整 DRC**（需 `klayout` 可执行文件）：

```bash
# 方式 1：脚本
chmod +x demo/run_demo.sh
./demo/run_demo.sh

# 方式 2：Python
PYTHONPATH=. python3 demo/chipx_p1_demo.py
```

可选参数：

```bash
./demo/run_demo.sh --output-dir demo/output --timeout 1200
./demo/run_demo.sh --no-mark-gds          # 只生成 .lyrdb
./demo/run_demo.sh --klayout-path /path/to/klayout
```

## 查看结果

```bash
klayout tests/chipx_tfln/data/P1-20240625-SYD-LN600E300[17X15]-ITLA-V1.5.gds \
  -m demo/output/P1_chipx.lyrdb
```

在 KLayout 菜单 **Verification → Marker Browser** 中按规则类别浏览违规。

标记版图 `P1_chipx_marked.gds` 在 GDS layer `10000+` 上按 DRC 类别绘制错误几何，便于在无 GUI 时检查。

## 输出目录

`demo/output/` 已加入 `.gitignore`，不会提交生成的 `.lyrdb` / `*_marked.gds`。
