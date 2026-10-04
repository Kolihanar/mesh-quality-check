# OpenFOAM 12 官方 motorBikeSteady 加层实测验证

在 WSL Ubuntu 24.04 使用已编译的 OpenFOAM Foundation 12，从 `tutorials/incompressibleFluid/motorBikeSteady` 复制独立算例，串行运行 `surfaceFeatures`、`blockMesh`、`snappyHexMesh -overwrite` 和 `checkMesh -allGeometry -allTopology`。官方 [`snappyHexMeshDict`](snappyHexMeshDict) 原本启用 `addLayers true` 和 `writeFlags (layerFields)`，本次没有修改加层参数。算例是**外流**，这里只验证真实 `nSurfaceLayers` 的解析、层覆盖率和原生网格问题的保留，不把它作为内流适用性验证。

## 复现命令

```bash
source "$HOME/OpenFOAM/OpenFOAM-12/etc/bashrc" ParaView_TYPE=none SCOTCH_TYPE=none ZOLTAN_TYPE=none
skill=/absolute/path/to/mesh-quality-check
case_dir="$HOME/OpenFOAM/${USER}-12/run/motorBikeSteady-layer-validation-20261004"
cp -a "$FOAM_TUTORIALS/incompressibleFluid/motorBikeSteady" "$case_dir"
cp "$FOAM_TUTORIALS/resources/geometry/motorBike.obj.gz" "$case_dir/constant/geometry/"
surfaceFeatures -case "$case_dir" > "$case_dir/log.surfaceFeatures" 2>&1
blockMesh -case "$case_dir" > "$case_dir/log.blockMesh" 2>&1
snappyHexMesh -case "$case_dir" -overwrite > "$case_dir/log.snappyHexMesh" 2>&1
checkMesh -case "$case_dir" -allGeometry -allTopology > "$case_dir/log.checkMesh" 2>&1
foamDictionary -case "$case_dir" system/controlDict -entry writeFormat -set ascii
foamFormatConvert -case "$case_dir" -constant > "$case_dir/log.foamFormatConvert" 2>&1
python3 "$skill/scripts/mesh_check.py" "$case_dir" \
  --context "$skill/validation/official_openfoam12_motorbike/context.json" \
  --checkmesh-log "$case_dir/log.checkMesh" \
  --layer-field "$case_dir/0/nSurfaceLayers" \
  -o "$skill/validation/official_openfoam12_motorbike"
python3 "$skill/validation/official_openfoam12_motorbike/verify.py"
```

官方算例的 `writeFormat` 原为 `binary`；格式转换仅在复制出的验证算例中进行。Skill 当前要求 ASCII `polyMesh` 和 ASCII 层字段。最后一个检查命令因报告高风险返回退出码 2，报告仍会完整写出。

## 对照结果

`snappyHexMesh` 生成 353,779 单元和 1,108,744 面，写出实际加层字段。[`log.checkMesh`](log.checkMesh) 报告 `Failed 4 mesh checks`：15 个高度歪斜面、73 个低行列式单元、15,226 个凹单元及 996 个低面插值权重面。Skill 的[报告](mesh_report.md)保留这些异常，并把低层覆盖率定位到完整部件名。

| patch | 原生面数 | 原始层字段中有层面数 | Skill 面积加权覆盖率 |
|---|---:|---:|---:|
| `lowerWall` | 5,341 | 5,307 | 99.994% |
| `motorBike_frt-fairing:001%1` | 5,292 | 2,056 | 39.675% |
| `motorBike_fr-wh-rim:011%11` | 492 | 154 | 34.676% |

[`context.json`](context.json) 只给这三个 patch 设置“至少 1 层、覆盖率至少 95%”的**验证目标**。原生日志的 `layers` 列是按面计数的平均层数；Skill 的覆盖率按壁面面积加权，所以数值无需相等。[`verify.py`](verify.py) 独立解析保存的 [`nSurfaceLayers.0`](nSurfaceLayers.0)、[`log.snappyHexMesh`](log.snappyHexMesh) 和 [`log.checkMesh`](log.checkMesh)，核对面数、有层面数、原生加层均值和报告结论。完整原始边界名见 [`boundary`](boundary)，网格文件哈希见 [`polyMesh.sha256`](polyMesh.sha256)。

真实算例还暴露并修复了一个解析缺陷：原先边界名中的 `:`、`%` 被截断，部件错误显示为 `1`、`11` 等数字。现在 `polyMesh/boundary` 与层字段的 patch 名保持一致，并有集成回归测试覆盖。
