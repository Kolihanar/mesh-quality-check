# OpenFOAM 12 官方封闭内流：实际加层与网格失败验证

2026-10-04 使用 OpenFOAM Foundation 12 官方 `tutorials/fluid/iglooWithFridges`。这是带温度场、`kEpsilon` 和壁面函数的封闭室内流动算例，原版 `snappyHexMeshDict` 已设置 `addLayers true`。验证副本只添加 `writeFlags (layerFields);`，让 OpenFOAM 写出实际逐壁面层数 `0/nSurfaceLayers`；再运行 `blockMesh`、`snappyHexMesh -overwrite` 和 `checkMesh -allGeometry -allTopology`。这是**加层网格验证**，不是管道压降或换热能量守恒的正例。

原生网格有 11,274 个单元。`snappyHexMesh` 结束时称网格生成完成，但完整 `checkMesh` 报告 **1 项失败：1,733 个凹单元（15.4%）**。Skill 将原生失败项标为高风险，并保留对凹单元、层数不足和近壁面质量的具体建议；没有把“网格生成结束”当作通过。由于网格检查未通过，本次没有继续运行热流求解器。

| 壁面 | 期望层数 | 有层面数 | 有层面积覆盖率 | 低于期望的面数 | 低于期望的面积 |
|---|---:|---:|---:|---:|---:|
| igloo | 1 | 1,276 / 1,276 | 100% | 0 | 0% |
| twoFridgeFreezers_seal_0 | 3 | 728 / 800 | 97.51% | 472 | 55.10% |
| twoFridgeFreezers_herring_1 | 3 | 586 / 592 | 99.27% | 348 | 57.88% |

冰柜壁面大多**至少有一层**，但超过一半面积没有达到设计的三层。`ground` 未被指定加层，实际为零层；Skill 没把它算成缺失三层的问题。图按真实边界面的面积统计，与 [`report/mesh_report.md`](report/mesh_report.md) 一致。

![真实室内壁面的层数分布与不足面积](actual_layers.png)

原始证据包括 [`log.snappyHexMesh`](log.snappyHexMesh)、[`log.checkMesh`](log.checkMesh)、[`nSurfaceLayers.0`](nSurfaceLayers.0)、[`points`](points)、[`faces`](faces)、[`boundary`](boundary) 与壁面场文件；[`native.sha256`](native.sha256) 保存逐文件哈希。[`verify.py`](verify.py) 不调用 Skill 的层统计函数，独立解析真实面、节点和层字段，复算每个壁面的层数、面数、面积加权覆盖率与不足面积，并与原生加层日志及 Skill 报告核对。它也验证 OpenFOAM 的 `wall` patch 组为各实际壁面继承 `nutkWallFunction`、`epsilonWallFunction` 和带 `compressible::` 前缀的 `alphat` 壁面函数。

## 复现

假设 OpenFOAM 12 位于 `~/OpenFOAM/OpenFOAM-12`，本 Skill 位于 `/absolute/path/to/mesh-quality-check`。准备脚本创建独立副本，若目标目录已存在则拒绝覆盖；复现时可先按需修改脚本中的日期后缀。

```bash
source "$HOME/OpenFOAM/OpenFOAM-12/etc/bashrc" ParaView_TYPE=none SCOTCH_TYPE=none ZOLTAN_TYPE=none
skill=/absolute/path/to/mesh-quality-check
python3 "$skill/validation/official_openfoam12_igloo/prepare.py"
case_dir="$HOME/OpenFOAM/${USER}-12/run/iglooWithFridges-layer-validation-20261004"
blockMesh -case "$case_dir" > "$case_dir/log.blockMesh" 2>&1
snappyHexMesh -case "$case_dir" -overwrite > "$case_dir/log.snappyHexMesh" 2>&1
checkMesh -case "$case_dir" -allGeometry -allTopology > "$case_dir/log.checkMesh" 2>&1
python3 "$skill/validation/official_openfoam12_igloo/collect.py"
python3 "$skill/scripts/mesh_check.py" "$case_dir" \
    --context "$skill/validation/official_openfoam12_igloo/context.json" \
    --checkmesh-log "$case_dir/log.checkMesh" \
    -o "$skill/validation/official_openfoam12_igloo/report"
python3 "$skill/validation/official_openfoam12_igloo/verify.py"
python3 "$skill/validation/official_openfoam12_igloo/plot.py"
```

Skill 预期返回退出码 2（高风险）。本次缺少流场求解结果、实际 y⁺、热流和能量收支，因此不能据此判断这个算例已可靠用于 CFD。下一步应先定位并减少凹单元，随后在冰柜贴体面和层终止处调整表面分辨率、层厚或层生长限制，再复查 `checkMesh`、逐面层数、近壁质量；网格通过后才开展温度场求解与能量验证。
