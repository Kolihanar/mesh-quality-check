# OpenFOAM 12 官方内流算例实测验证

2026-10-04 在 WSL Ubuntu 24.04 运行 OpenFOAM Foundation 12 的 `tutorials/incompressibleFluid/pitzDailySteady`。它是二维、单相 RANS 内流算例；`momentumTransport` 使用 `kEpsilon`，壁面使用 `nutkWallFunction` 和 `epsilonWallFunction`。本目录的日志和 yPlus 场来自实际运行，区别于 [`../summary.md`](../summary.md) 的合成样例。

源码从用户指定的 [CFD-China 国内镜像介绍](https://www.cfd-china.com/topic/4144/openfoam%E5%9B%BD%E5%86%85%E4%B8%8B%E8%BD%BD%E5%9C%B0%E5%9D%80-%E6%BB%A1%E9%80%9F) 下载。镜像的 OpenFOAM-12 源码和脚本内容与 [官方 OpenFOAM-12 仓库](https://github.com/OpenFOAM/OpenFOAM-12) 的 `8ecfbe007e8ee9c4d8c26b7983919837bf179ad5` 版本逐文件核对一致；ThirdParty-12 内容与官方 `cab725f5e7929e8f5ec35c54edc493a822355235` 核对一致。镜像另外添加了说明文件和自身 Git 历史。首次验证时所需的 `blockMesh`、`checkMesh`、`foamRun`、`foamPostProcess` 与 `incompressibleFluid` 模块已编译；随后用户完成其余编译，本次又确认 `snappyHexMesh` 和 `surfaceFeatures` 可用。

## 复现

下面命令假设 OpenFOAM-12 位于 `~/OpenFOAM/OpenFOAM-12`，本 Skill 位于 `/absolute/path/to/mesh-quality-check`，已编译上述程序及模块。先复制算例并保留计算前快照，再生成原生日志与结果：

```bash
source "$HOME/OpenFOAM/OpenFOAM-12/etc/bashrc" ParaView_TYPE=none SCOTCH_TYPE=none ZOLTAN_TYPE=none
skill=/absolute/path/to/mesh-quality-check
case_dir="$HOME/OpenFOAM/${USER}-12/run/pitzDailySteady-mesh-quality-20261004"
pre_dir="$HOME/OpenFOAM/${USER}-12/run/pitzDailySteady-mesh-quality-preflight"
cp -a "$FOAM_TUTORIALS/incompressibleFluid/pitzDailySteady" "$case_dir"
blockMesh -case "$case_dir" > "$case_dir/log.blockMesh" 2>&1
checkMesh -case "$case_dir" -allGeometry -allTopology > "$case_dir/log.checkMesh" 2>&1
mkdir -p "$pre_dir"
cp -a "$case_dir/0" "$case_dir/constant" "$case_dir/system" "$pre_dir/"
cp "$case_dir/log.checkMesh" "$pre_dir/log.checkMesh"
python3 "$skill/scripts/mesh_check.py" "$pre_dir" --context "$skill/validation/official_openfoam12/context.json" --checkmesh-log "$pre_dir/log.checkMesh" -o "$skill/validation/official_openfoam12/preflight"
foamRun -case "$case_dir" > "$case_dir/log.foamRun" 2>&1
foamPostProcess -case "$case_dir" -solver incompressibleFluid -func yPlus -latestTime > "$case_dir/log.yPlus.solver" 2>&1
cp "$skill/validation/official_openfoam12/functions" "$case_dir/system/validationFunctions"
foamPostProcess -case "$case_dir" -solver incompressibleFluid -dict system/validationFunctions -latestTime > "$case_dir/log.surfaceFieldValue" 2>&1
python3 "$skill/validation/official_openfoam12/extract_phi.py" "$case_dir/286/phi" > "$skill/validation/official_openfoam12/flow_evidence.json"
python3 "$skill/scripts/mesh_check.py" "$case_dir" --context "$skill/validation/official_openfoam12/postflight_context.json" --checkmesh-log "$case_dir/log.checkMesh" -o "$skill/validation/official_openfoam12/postflight"
python3 "$skill/validation/official_openfoam12/verify.py"
```

`foamPostProcess` 在此版本需要 `-solver incompressibleFluid` 才能创建湍流模型。首次运行后，按 `flow_evidence.json` 的实际数值更新 `postflight_context.json` 中的体积通量；本次保存的值对应时间 286。Skill 的 `overall=high` 时 CLI 返回 2，这是发现超出筛查目标的预期退出状态。

## 对照结果

| 证据 | OpenFOAM 原生输出 | Skill 报告 |
|---|---:|---:|
| 网格 | 12,225 单元；49,180 面；25,012 点；`Mesh OK` | 数量一致，`checkMesh` 结论一致，无规模冲突 |
| 最大非正交角 / 歪斜度 | 5.95045° / 0.260575 | 5.95° / 0.2606（报告显示精度） |
| 稳态求解 | SIMPLE 在 286 次迭代后报告收敛 | 从 `286/yPlus` 自动读取试算后场 |
| upperWall y⁺ 最小/最大 | 2.81891 / 7.24148 | 完全一致，223/223 面低于本次 30–300 目标 |
| lowerWall y⁺ 最小/最大 | 0.334426 / 26.5139 | 完全一致，250/250 面低于本次 30–300 目标 |
| 入口/出口体积通量 | −2.539999×10⁻⁴ / +2.540073×10⁻⁴ m³/s | 从 ASCII `phi` 得到 −2.5399992×10⁻⁴ / +2.54007287×10⁻⁴ m³/s，差异仅为原生表格的显示舍入 |
| 体积通量相对不平衡 | 约 0.0029% | 0.0029003%，低于本次 1% 容差；恒密度流可据此核对质量守恒 |

原始材料：[`log.checkMesh`](log.checkMesh)、[`log.foamRun`](log.foamRun)、[`log.yPlus.solver`](log.yPlus.solver)、[`yPlus.286`](yPlus.286)、[`phi.286`](phi.286)、[`log.surfaceFieldValue`](log.surfaceFieldValue)、[`inletFlow.dat`](inletFlow.dat)、[`outletFlow.dat`](outletFlow.dat)、[`polyMesh.sha256`](polyMesh.sha256)。报告：[`preflight/mesh_report.md`](preflight/mesh_report.md)、[`postflight/mesh_report.md`](postflight/mesh_report.md)。[`extract_phi.py`](extract_phi.py) 读取并核对 `phi` 量纲；[`verify.py`](verify.py) 比较原生日志、yPlus 场、原生通量表和 Skill 报告。

本次在 [`context.json`](context.json) **显式选择** 30–300 作为壁面 y⁺ 筛查目标，因此报告将两面标为高风险的“目标偏离”。这不是 OpenFOAM 对该算例的硬性有效性规则。OpenFOAM 12 的 [`nutkWallFunction`](https://cpp.openfoam.org/v12/nutkWallFunctionFvPatchScalarField_8C_source.html) 和 [`epsilonWallFunction`](https://cpp.openfoam.org/v12/epsilonWallFunctionFvPatchScalarField_8C_source.html) 均包含低 y⁺ 分支；而原生求解已报告收敛。因此不能由 y⁺ 低于 30 推断算例发散，也不能由收敛和守恒推断压降或壁面剪切足够准确。原生入口/出口平均运动压力已保存于 [`inletPressure.dat`](inletPressure.dat) 与 [`outletPressure.dat`](outletPressure.dat)，但只有一个时间点；后续已完成[三网格目标量监测验证](../official_openfoam12_grid/README.md)。

此算例没有 `snappyHexMesh` 加层字段；实际层读取另见 [motorBikeSteady 外流教程的独立验证](../official_openfoam12_motorbike/README.md)。尚未验证换热、能量守恒或目标量稳定后的网格收敛。
