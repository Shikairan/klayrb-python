# Chipx TFLN + P1 样例 Demo

1. DRC → `P1_chipx.lyrdb`
2. 分 layer 方框标注 → `P1_chipx_annotated.gds`（layer 10000+）
3. 对照表 → `P1_chipx_annotated_layer_map.csv`（仅 layer ↔ 错误表格）

## 运行

```bash
./demo/run_demo.sh
```

## CSV 格式

仅表头 + 数据行，无注释：

```csv
layer,datatype,rule_id,error
10000,0,LD_FC_COR_S,ld_fc_cor space < 1 nm
10001,0,M1_S,M1 space < 0.4 µm
```

列说明：`layer` / `datatype` 对应 GDS 层；`rule_id` 为规则 ID；`error` 为 lyrdb 中的错误描述。
