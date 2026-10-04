# 网格质量检查报告

- 生成时间：2026-10-04 19:32:21
- 输入：`/home/foamuser/OpenFOAM/foamuser-12/run/iglooWithFridges-layer-validation-20261004`
- 识别结果：**OpenFOAM**（case）——找到 constant/polyMesh/{points,faces,owner}；存在 system/controlDict

## 结论：🔴 高风险

已检查指标存在高风险偏离；需结合实际边界条件及目标量验证其影响。

CFD 适用性判断：**高风险指标待复核，关键结果证据不足**。

checkMesh 自身结论：`Failed 1 mesh checks`

## 1. 网格基本信息

| 项目 | 值 |
|---|---|
| 单元数 | 11274 |
| 面数 | 37893 |
| 内部面数 | 34307 |
| 节点数 | 15906 |
| 维度 | 3D |
| OpenFOAM 版本 | 12 |
| 单元类型 | hexahedra 7643，prisms 208，tet wedges 12，polyhedra 3411 |
| 包围盒 | [-1.00389, -1.00395, 0.0] → [7.00389, 7.00395, 4.0] |
| 单元体积 | 最小 2.147e-05，最大 0.1351 |
| 边界 | maxY[symmetryPlane](0)，minX[symmetryPlane](0)，maxX[symmetryPlane](0)，minY[symmetryPlane](0)，ground[wall](918)，maxZ[symmetryPlane](0)，igloo[wall](1276)，twoFridgeFreezers_seal_0[wall](800)，twoFridgeFreezers_herring_1[wall](592) |

## 2. 致命/拓扑问题

- 🔴 **checkMesh 检查失败项**（高风险）：范围 未知（只有极值），极值 1

## 3. CFD 适用性与近壁检查

当前范围：OpenFOAM 单相 RANS 内流。计算前 y⁺ 为估算，已有试算的 yPlus 场为求解后证据。

算例识别：求解器 foamRun；湍流类型 RAS；模型 kEpsilon。

| 壁面 | 首层中心距：最小/中位/P95 | y⁺ 证据 | y⁺：P05/中位/P95 | 目标 | 区间外面积 |
|---|---|---|---|---|---|
| ground | 0.03115/0.06301/0.2522 | 待补全 | —/—/— | 待指定 | — |
| igloo | 0.06156/0.06176/0.06181 | 待补全 | —/—/— | 待指定 | — |
| twoFridgeFreezers_seal_0 | 0.003495/0.01763/0.02892 | 待补全 | —/—/— | 待指定 | — |
| twoFridgeFreezers_herring_1 | 0.006843/0.02295/0.02965 | 待补全 | —/—/— | 待指定 | — |

表中 y⁺ 目标是所选工况的筛查区间，区间外比例表示目标偏离，并不单独证明求解失败或结果不可靠。首层中心距按单元中心到边界面平面的法向投影计算。近壁层数与覆盖率需要实际生成记录或可识别的层字段；规则六面体的连续排列不直接算作边界层。

- ground 壁面场类型：nut=nutkWallFunction、epsilon=epsilonWallFunction、alphat=compressible::alphatJayatillekeWallFunction
- ground：OpenFOAM 12 的 nutkWallFunction / epsilonWallFunction 含低 y⁺ 分支；低于筛查下限时先核对实际分支、壁面剪切及压降/换热的网格敏感性，再决定是否调整首层尺寸。
- ground 首层相邻内部面：非正交角最大 47.71°、>70° 0 面；歪斜度最大 0.6501、>4 0 面；首层单元长宽比 P95 3.101。
- igloo 壁面场类型：nut=nutkWallFunction、epsilon=epsilonWallFunction、alphat=compressible::alphatJayatillekeWallFunction
- igloo：OpenFOAM 12 的 nutkWallFunction / epsilonWallFunction 含低 y⁺ 分支；低于筛查下限时先核对实际分支、壁面剪切及压降/换热的网格敏感性，再决定是否调整首层尺寸。
- igloo 首层相邻内部面：非正交角最大 34.29°、>70° 0 面；歪斜度最大 0.4483、>4 0 面；首层单元长宽比 P95 2.058。
- twoFridgeFreezers_seal_0 壁面场类型：nut=nutkWallFunction、epsilon=epsilonWallFunction、alphat=compressible::alphatJayatillekeWallFunction
- twoFridgeFreezers_seal_0：OpenFOAM 12 的 nutkWallFunction / epsilonWallFunction 含低 y⁺ 分支；低于筛查下限时先核对实际分支、壁面剪切及压降/换热的网格敏感性，再决定是否调整首层尺寸。
- twoFridgeFreezers_seal_0 首层相邻内部面：非正交角最大 40.86°、>70° 0 面；歪斜度最大 0.6834、>4 0 面；首层单元长宽比 P95 5.009。
- twoFridgeFreezers_herring_1 壁面场类型：nut=nutkWallFunction、epsilon=epsilonWallFunction、alphat=compressible::alphatJayatillekeWallFunction
- twoFridgeFreezers_herring_1：OpenFOAM 12 的 nutkWallFunction / epsilonWallFunction 含低 y⁺ 分支；低于筛查下限时先核对实际分支、壁面剪切及压降/换热的网格敏感性，再决定是否调整首层尺寸。
- twoFridgeFreezers_herring_1 首层相邻内部面：非正交角最大 46.53°、>70° 0 面；歪斜度最大 0.9969、>4 0 面；首层单元长宽比 P95 4.957。
**边界层实测数据**

- ground：实际层数最小值 0，覆盖率 0.0%，面积加权平均层数 0，有层面数 0/918（来自snappyHexMesh nSurfaceLayers 边界场）
- igloo：实际层数最小值 1，覆盖率 100.0%，面积加权平均层数 1，有层面数 1276/1276，低于目标的面积比例 0.0%（来自snappyHexMesh nSurfaceLayers 边界场）
- twoFridgeFreezers_seal_0：实际层数最小值 0，覆盖率 97.5%，面积加权平均层数 2.138，有层面数 728/800，低于目标的面积比例 55.1%（来自snappyHexMesh nSurfaceLayers 边界场）
- twoFridgeFreezers_herring_1：实际层数最小值 0，覆盖率 99.3%，面积加权平均层数 2.105，有层面数 586/592，低于目标的面积比例 57.9%（来自snappyHexMesh nSurfaceLayers 边界场）

**待补全的关键证据**

- 缺少与当前网格匹配且结论为 Mesh OK 的完整 checkMesh 检查
- 壁面 ground 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 igloo 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 twoFridgeFreezers_seal_0 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 twoFridgeFreezers_herring_1 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 缺少试算后各入口/出口的有符号质量通量（或恒密度流的体积通量），无法核对质量守恒
- 换热算例缺少有符号焓流与壁面热流，无法核对能量守恒
- 缺少压降、流量或换热量的监测序列，无法复核结果稳定性
- 缺少至少三套网格的同一目标量结果，无法检查网格敏感性

## 4. 质量指标

| 指标 | 极值 | 阈值（中等/高/致命） | 超标范围 | 等级 |
|---|---|---|---|---|
| 凹单元 |  — | — | 1733 个单元（15.4%，大面积） | 🟡 中等 |
| 非正交性 | 最大 50.53° | > 65/70/85 | 0 | 🟢 可接受 |
| 歪斜度（OpenFOAM 定义） | 最大 3.448 | > 2.5/4/20 | 0 | 🟡 中等 |
| 长宽比 | 最大 11.38 | > 1000/10000/— | 0 | 🟢 可接受 |
| 单元行列式 | 最小 0.01849 | < 0.01/0.001/— | 0 | 🟢 可接受 |
| 面插值权重 | 最小 0.06032 | < 0.05/0.02/— | 0 | 🟢 可接受 |
| 相邻单元体积比 | 最小 0.01797 | < 0.01/0.001/— | 0 | 🟢 可接受 |
| 壁面 ground 的近壁内部面非正交角 | 最大 47.71° | — | 0 | 🟢 可接受 |
| 壁面 ground 的近壁内部面歪斜度 | 最大 0.6501 | — | 0 | 🟢 可接受 |
| 壁面 igloo 实际边界层层数 | 最小 1 | — | 0 | 🟢 可接受 |
| 壁面 igloo 边界层覆盖率 |  1 | — | 0 | 🟢 可接受 |
| 壁面 igloo 的近壁内部面非正交角 | 最大 34.29° | — | 0 | 🟢 可接受 |
| 壁面 igloo 的近壁内部面歪斜度 | 最大 0.4483 | — | 0 | 🟢 可接受 |
| 壁面 twoFridgeFreezers_seal_0 实际边界层层数 | 最小 0 | — | 472 个壁面面（59%，大面积） | 🔴 高风险 |
| 壁面 twoFridgeFreezers_seal_0 边界层覆盖率 |  0.9751 | — | 72 个壁面面（9%，大面积） | 🟢 可接受 |
| 壁面 twoFridgeFreezers_seal_0 的近壁内部面非正交角 | 最大 40.86° | — | 0 | 🟢 可接受 |
| 壁面 twoFridgeFreezers_seal_0 的近壁内部面歪斜度 | 最大 0.6834 | — | 0 | 🟢 可接受 |
| 壁面 twoFridgeFreezers_herring_1 实际边界层层数 | 最小 0 | — | 348 个壁面面（58.8%，大面积） | 🔴 高风险 |
| 壁面 twoFridgeFreezers_herring_1 边界层覆盖率 |  0.9927 | — | 6 个壁面面（1.01%，大面积） | 🟢 可接受 |
| 壁面 twoFridgeFreezers_herring_1 的近壁内部面非正交角 | 最大 46.53° | — | 0 | 🟢 可接受 |
| 壁面 twoFridgeFreezers_herring_1 的近壁内部面歪斜度 | 最大 0.9969 | — | 0 | 🟢 可接受 |

- **非正交性**：平均值 14.73°；分布：>50°: 1，>65°: 0，>70°: 0，>80°: 0；定义：面法向与相邻单元中心连线的夹角（仅内部面），0° 为理想
- **歪斜度（OpenFOAM 定义）**：分布：>1: 70，>2.5: 4，>4: 0，>10: 0；定义：面中心相对两单元中心连线交点的偏移，按面尺寸归一化；无上界，0 为理想
- **长宽比**：定义：OpenFOAM cellAspectRatio，1 为理想
- **壁面 ground 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 ground 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 igloo 实际边界层层数**：定义：目标至少 1 层；按面积计算不足比例 0.0%；来自 nSurfaceLayers 边界场
- **壁面 igloo 边界层覆盖率**：定义：目标不低于 0.95；按壁面面积加权；来自 nSurfaceLayers 边界场
- **壁面 igloo 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 igloo 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 twoFridgeFreezers_seal_0 实际边界层层数**：定义：目标至少 3 层；按面积计算不足比例 55.1%；来自 nSurfaceLayers 边界场
- **壁面 twoFridgeFreezers_seal_0 边界层覆盖率**：定义：目标不低于 0.95；按壁面面积加权；来自 nSurfaceLayers 边界场
- **壁面 twoFridgeFreezers_seal_0 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 twoFridgeFreezers_seal_0 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 twoFridgeFreezers_herring_1 实际边界层层数**：定义：目标至少 3 层；按面积计算不足比例 57.9%；来自 nSurfaceLayers 边界场
- **壁面 twoFridgeFreezers_herring_1 边界层覆盖率**：定义：目标不低于 0.95；按壁面面积加权；来自 nSurfaceLayers 边界场
- **壁面 twoFridgeFreezers_herring_1 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 twoFridgeFreezers_herring_1 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标

## 5. 问题定位

**壁面 twoFridgeFreezers_seal_0 实际边界层层数**
- 靠近边界：twoFridgeFreezers_seal_0（472）
- 包围盒：[1.9999999999999996, 1.9999999999999993, 0.03205448818642295] → [3.000000000000001, 3.000000000000001, 2.100000000000001]

**壁面 twoFridgeFreezers_herring_1 实际边界层层数**
- 靠近边界：twoFridgeFreezers_herring_1（348）
- 包围盒：[3.4999999999999996, 2.999999999999999, 0.06200743770040226] → [4.500000000000001, 4.000000000000001, 2.1]

可视化：checkMesh 会把坏面/坏单元写成集合（如 nonOrthoFaces、skewFaces）。用 `foamToVTK -faceSet nonOrthoFaces`（单元集合用 -cellSet）转成 VTK，或 ESI 版直接用 `checkMesh -allGeometry -allTopology -writeSets vtk`，在 ParaView 中查看。

## 6. 按优先级排列的网格优化建议

1. **checkMesh 检查失败项**（高风险）
   - 位置：报告未提供局部坐标；先用 checkMesh 集合或质量场定位
   - 证据：极值 1
   - 修改：本次原生失败项包含凹单元：先检查贴体表面转角、窄缝、层终止处和相邻细化级别的过渡，再按局部位置调整表面网格、层厚和层生长限制；不要仅凭 snappyHexMesh 的完成信息放行。
   - 验证：重新运行 checkMesh -allGeometry -allTopology，确认 Failed mesh checks 归零。
2. **壁面 twoFridgeFreezers_seal_0 实际边界层层数**（高风险）
   - 位置：边界 twoFridgeFreezers_seal_0，坐标范围 [1.9999999999999996, 1.9999999999999993, 0.03205448818642295] 至 [3.000000000000001, 3.000000000000001, 2.100000000000001]
   - 证据：极值 0；范围 472 / 800；目标至少 3 层；按面积计算不足比例 55.1%；来自 nSurfaceLayers 边界场
   - 修改：在低于目标层数的壁面区域检查尖角、狭缝及贴体面尺寸；核对 snappyHexMesh 的 minThickness、featureAngle 与层末端缓冲设置，再局部重划。
   - 验证：重新读取 nSurfaceLayers 边界场，确认低于目标层数的面积比例与位置改善，并复查近壁歪斜和非正交性。
3. **壁面 twoFridgeFreezers_herring_1 实际边界层层数**（高风险）
   - 位置：边界 twoFridgeFreezers_herring_1，坐标范围 [3.4999999999999996, 2.999999999999999, 0.06200743770040226] 至 [4.500000000000001, 4.000000000000001, 2.1]
   - 证据：极值 0；范围 348 / 592；目标至少 3 层；按面积计算不足比例 57.9%；来自 nSurfaceLayers 边界场
   - 修改：在低于目标层数的壁面区域检查尖角、狭缝及贴体面尺寸；核对 snappyHexMesh 的 minThickness、featureAngle 与层末端缓冲设置，再局部重划。
   - 验证：重新读取 nSurfaceLayers 边界场，确认低于目标层数的面积比例与位置改善，并复查近壁歪斜和非正交性。
4. **凹单元**（中等）
   - 位置：报告未提供局部坐标；先用 checkMesh 集合或质量场定位
   - 证据：极值 None；范围 1733 / 11274
   - 修改：检查贴体面尖角、狭缝、层终止处及相邻细化级别的过渡；按问题区域调整表面分辨率、层厚和层生长限制后重新划分。
   - 验证：重新运行完整 checkMesh，比较凹单元数量及失败检查项，并复核加层覆盖率。
5. **歪斜度（OpenFOAM 定义）**（中等）
   - 位置：报告未提供局部坐标；先用 checkMesh 集合或质量场定位
   - 证据：极值 3.4481；范围 0 / 37893；面中心相对两单元中心连线交点的偏移，按面尺寸归一化；无上界，0 为理想
   - 修改：定位歪斜面的邻接单元，清理尖角/窄缝，平滑表面尺寸过渡并重新贴体。
   - 验证：重新检查超标面数、分布和最大歪斜度。

**下一步取证**

- 缺少与当前网格匹配且结论为 Mesh OK 的完整 checkMesh 检查
- 壁面 ground 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 igloo 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 twoFridgeFreezers_seal_0 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 twoFridgeFreezers_herring_1 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 缺少试算后各入口/出口的有符号质量通量（或恒密度流的体积通量），无法核对质量守恒
- 换热算例缺少有符号焓流与壁面热流，无法核对能量守恒
- 缺少压降、流量或换热量的监测序列，无法复核结果稳定性
- 缺少至少三套网格的同一目标量结果，无法检查网格敏感性
- 已有试算时，可用 OpenFOAM 的 `yPlus` 功能对象输出壁面场；提供该 ASCII 场用于逐壁面复核。

## 7. 原始报警行

```
*There are 245 faces with concave angles between consecutive edges. Max concave angle = 39.253 degrees.
***Concave cells (using face planes) found, number of cells: 1733
```

## 8. 局限与说明

- 位置/分布统计来自本工具按 OpenFOAM 公式的独立计算，数值可能与 checkMesh 有微小差别；严重程度以 checkMesh 数值为准。
- 阈值为经验值（见 `scripts/thresholds.json`），严重程度需结合求解类型判断：同样的指标对稳态 RANS 和瞬态多相/动网格计算的影响不同。

## 9. 检查日志

| 时间(s) | 状态 | 步骤 | 命令 |
|---|---|---|---|
| 0.0 | ok | 识别网格来源：openfoam / case（找到 constant/polyMesh/{points,faces,owner}；存在 system/controlDict） |  |
| 0.05 | ok | 使用已有 checkMesh 日志：/home/foamuser/OpenFOAM/foamuser-12/run/iglooWithFridges-layer-validation-20261004/log.checkMesh |  |
| 0.05 | ok | 用 Python 读取 polyMesh，计算各面/单元指标分布和位置 | `polymesh.analyse(/home/foamuser/OpenFOAM/foamuser-12/run/iglooWithFridges-layer-validation-20261004/constant/polyMesh)` |
| 0.5 | ok | polyMesh 读取完成：11274 个单元，37893 个面 |  |
