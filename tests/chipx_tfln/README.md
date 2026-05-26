# Chipx TFLN DRC 集成测试

本目录专门用于 **Chipx LNOI** 规则与样例版图的端到端测试：

| 文件 | 路径 |
|------|------|
| DRC 规则 | 仓库根目录 [`Chipx_TFLN_DRC_QCI-V16-20240415.lydrc`](../../Chipx_TFLN_DRC_QCI-V16-20240415.lydrc) |
| 样例 GDS | [`data/P1-20240625-SYD-LN600E300[17X15]-ITLA-V1.5.gds`](data/P1-20240625-SYD-LN600E300%5B17X15%5D-ITLA-V1.5.gds) |

## 运行

需安装 **KLayout 可执行文件**（`klayout` 在 `PATH`）及 Python 依赖：

```bash
pip install -r requirements.txt
PYTHONPATH=. python3 -m pytest tests/chipx_tfln/ -v
```

仅跑无需 `klayout` 的用例（资源检查、lydrc 解析等）：

```bash
PYTHONPATH=. python3 -m pytest tests/chipx_tfln/ -v -m "not chipx_drc"
```

## 输出

集成测试在临时目录生成 `.lyrdb`、`*_marked.gds`，不提交到 Git。本地调试可设置环境变量保留输出：

```bash
export KLAYRB_CHIPX_KEEP_OUTPUT=1
```
