# 用 OpenFOAM 官方算例验证

选用与当前安装相同版本的 `$FOAM_TUTORIALS`，在安装了 OpenFOAM 的环境运行。官方仓库保存的是算例设置，`polyMesh`、`nSurfaceLayers` 和 `yPlus` 需实际运行后生成。

## 已完成：OpenFOAM 12 pitzDailySteady

已在 WSL Ubuntu 24.04 用 Foundation 12 的 [`incompressibleFluid/pitzDailySteady`](https://github.com/OpenFOAM/OpenFOAM-12/tree/master/tutorials/incompressibleFluid/pitzDailySteady) 实际运行 `blockMesh`、`checkMesh -allGeometry -allTopology`、`foamRun`、`yPlus` 和入口出口 `surfaceFieldValue` 后处理。原生日志、两阶段报告、独立核对脚本和完整复现命令见 [`../validation/official_openfoam12/README.md`](../validation/official_openfoam12/README.md)。网格为 12,225 单元，`Mesh OK`；SIMPLE 报告在 286 次迭代后收敛。Skill 的网格规模、两面 y⁺ 极值及体积通量守恒与原生输出一致。

本次特意用 30–300 作为筛查目标以检验目标偏离检测。原生边界条件有低 y⁺ 分支，区间外标记应与实际边界条件、目标量和网格敏感性一起解读。该算例没有 `nSurfaceLayers`，故不能验证加层读取功能。

## 已完成：OpenFOAM 12 pitzDailySteady 三网格目标量监测

从同一官方教程只调整五个 block 的单元数，建立 5,446、12,225、27,703 单元三套网格。每套均通过原生 `checkMesh` 并由 `foamRun` 报告 SIMPLE 收敛；原生 `surfaceFieldValue` 逐迭代记录运动压力差与进出口体积通量。压力目标量在各套网格的末段仍漂移 2.03%、6.49%、8.21%，细/中末次值相差 12.80%。随后在三套独立副本收紧残差条件并续算至 1000 步：细网格末两段均值漂移降至 0.27%，但末段 P05–P95 跨度仍达 1.81%，超过 1% 筛查容差。Skill 新增末段波动检查，继续将网格比较标为初步结果。原生表格、两轮图、复现脚本与独立报告核对见 [`../validation/official_openfoam12_grid/README.md`](../validation/official_openfoam12_grid/README.md)。这项验证证明异常识别能力，尚不构成“已有网格收敛”的正例。

## 已完成：OpenFOAM 12 motorBikeSteady 加层字段

使用 Foundation 12 的 `tutorials/incompressibleFluid/motorBikeSteady` 原有 `addLayers true` / `layerFields` 设置，实际运行 `snappyHexMesh`，将二进制结果转为 ASCII 后，用本 Skill 读取真实 `nSurfaceLayers`。原生日志、字段、完整边界名、报告、复现命令和独立核对脚本见 [`../validation/official_openfoam12_motorbike/README.md`](../validation/official_openfoam12_motorbike/README.md)。真实网格的 `checkMesh` 报告 4 项失败，本工具保留这些问题并按完整 patch 名定位局部缺层。此教程是**外流**，仅证明层字段读写和定位，不用于验证内流 CFD 适用性。

## 已完成：OpenFOAM 12 iglooWithFridges 封闭内流加层

官方 `fluid/iglooWithFridges` 是含温度场的封闭室内 RANS 算例，原配置启用加层。验证副本只增加实际层字段输出，运行 `blockMesh`、`snappyHexMesh -overwrite` 和完整 `checkMesh`。11,274 单元中原生检查发现 1,733 个凹单元并报告 1 项失败；Skill 保留失败结论。冰柜两个壁面的“至少有一层”面积覆盖率为 97.51%、99.27%，但低于期望三层的面积为 55.10%、57.88%。原始字段、面面积独立重算、图和报告见 [`../validation/official_openfoam12_igloo/README.md`](../validation/official_openfoam12_igloo/README.md)。网格尚未通过检查，不能拿它作求解和能量守恒的正例。

## 可选扩展：OpenFOAM 10 pitzDaily

[OpenFOAM-10 官方 pitzDaily](https://github.com/OpenFOAM/OpenFOAM-10/tree/master/tutorials/incompressible/simpleFoam/pitzDaily) 是 `simpleFoam` 算例。复制到独立工作目录，运行其 `Allrun` 或先运行 `blockMesh` 和 `checkMesh -allGeometry -allTopology`。用本工具检查生成的算例目录，确认网格拓扑、近壁几何与未提供证据的提示符合预期。该算例没有 snappyHexMesh 加层输出，不能用于验证 `nSurfaceLayers` 自动读取。

```bash
cp -r "$FOAM_TUTORIALS/incompressible/simpleFoam/pitzDaily" ./pitzDaily-validation
cd ./pitzDaily-validation
blockMesh
checkMesh -allGeometry -allTopology > log.checkMesh
python /path/to/mesh-quality-check/scripts/mesh_check.py . --checkmesh-log log.checkMesh -o mesh_check_report
```

若试算后要验证 `yPlus`，须在该算例实际湍流模型与壁面条件下运行求解器及 `yPlus` 功能对象，再用 `--yplus-field` 指定输出。不能将没有实际生成的 yPlus 写入验证结论。

## 可选扩展：OpenFOAM 10 motorBike

[OpenFOAM-10 官方 motorBike 的 snappyHexMeshDict](https://github.com/OpenFOAM/OpenFOAM-10/blob/master/tutorials/incompressible/simpleFoam/motorBike/system/snappyHexMeshDict) 启用了 `addLayers true` 和 `writeFlags` 中的 `layerFields`，可验证生成后的 `nSurfaceLayers` 边界场解析、各壁面层覆盖率及缺层定位。它是**外流**，只用于层字段读写验证，不能据此验证内流适用性结论。用串行方式生成网格，避免并行的 `processor*` 字段需要先重构：

```bash
cp -r "$FOAM_TUTORIALS/incompressible/simpleFoam/motorBike" ./motorBike-validation
cd ./motorBike-validation
cp "$FOAM_TUTORIALS/resources/geometry/motorBike.obj.gz" constant/geometry/
surfaceFeatures
blockMesh
snappyHexMesh -overwrite > log.snappyHexMesh
checkMesh -allGeometry -allTopology > log.checkMesh
python /path/to/mesh-quality-check/scripts/mesh_check.py . \
  --checkmesh-log log.checkMesh -o mesh_check_report
```

工具会读取刚生成的 `checkMesh` 日志并自动寻找层字段；若自动寻找失败，可显式添加 `--layer-field /实际路径/nSurfaceLayers`。若字段为 binary，先用 OpenFOAM 导出为 ASCII。检查报告中的 `cfd.evidence`、`wall_checks.<patch>.layer_distribution` 和 `cfd.missing`，并与 snappyHexMesh 完成时的层统计对照；日志的平均层数按面计数，报告的平均值按面积加权，二者不必相等。
