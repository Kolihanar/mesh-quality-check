# 网格质量检查报告

- 生成时间：2026-10-04 17:40:16
- 输入：`/home/foamuser/OpenFOAM/foamuser-12/run/pitzDailySteady-mesh-quality-preflight`
- 识别结果：**OpenFOAM**（case）——找到 constant/polyMesh/{points,faces,owner}；存在 system/controlDict

## 结论：🟢 可接受

已执行的网格质量指标未见超限；完整 CFD 适用性见下方证据检查。

CFD 适用性判断：**关键近壁证据不足**。

checkMesh 自身结论：`Mesh OK`

## 1. 网格基本信息

| 项目 | 值 |
|---|---|
| 单元数 | 12225 |
| 面数 | 49180 |
| 内部面数 | 24170 |
| 节点数 | 25012 |
| 维度 | 2D |
| OpenFOAM 版本 | 12 |
| 单元类型 | hexahedra 12225 |
| 包围盒 | [-0.0206, -0.0254, -0.0005] → [0.29, 0.0254, 0.0005] |
| 单元体积 | 最小 1.690e-10，最大 3.836e-09 |
| 边界 | inlet[patch](30)，outlet[patch](57)，upperWall[wall](223)，lowerWall[wall](250)，frontAndBack[empty](24450) |

## 2. 致命/拓扑问题

本次已执行的检查中未报告致命拓扑问题；未执行的检查见局限与说明。


## 3. CFD 适用性与近壁检查

当前范围：OpenFOAM 单相 RANS 内流。计算前 y⁺ 为估算，已有试算的 yPlus 场为求解后证据。

算例识别：求解器 foamRun；湍流类型 RAS；模型 kEpsilon。

| 壁面 | 首层中心距：最小/中位/P95 | y⁺ 证据 | y⁺：P05/中位/P95 | 目标 | 区间外面积 |
|---|---|---|---|---|---|
| upperWall | 8.520e-05/1.817e-04/2.101e-04 | 待补全 | —/—/— | [30.0, 300.0] | — |
| lowerWall | 1.594e-04/5.138e-04/5.612e-04 | 待补全 | —/—/— | [30.0, 300.0] | — |

表中 y⁺ 目标是所选工况的筛查区间，区间外比例表示目标偏离，并不单独证明求解失败或结果不可靠。首层中心距按单元中心到边界面平面的法向投影计算。近壁层数与覆盖率需要实际生成记录或可识别的层字段；规则六面体的连续排列不直接算作边界层。

- upperWall 壁面场类型：nut=nutkWallFunction、omega=omegaWallFunction、epsilon=epsilonWallFunction
- upperWall：OpenFOAM 12 的 nutkWallFunction / epsilonWallFunction 含低 y⁺ 分支；低于筛查下限时先核对实际分支、壁面剪切及压降/换热的网格敏感性，再决定是否调整首层尺寸。
- upperWall 首层相邻内部面：非正交角最大 5.95°、>70° 0 面；歪斜度最大 0.1306、>4 0 面；首层单元长宽比 P95 7.134。
- lowerWall 壁面场类型：nut=nutkWallFunction、omega=omegaWallFunction、epsilon=epsilonWallFunction
- lowerWall：OpenFOAM 12 的 nutkWallFunction / epsilonWallFunction 含低 y⁺ 分支；低于筛查下限时先核对实际分支、壁面剪切及压降/换热的网格敏感性，再决定是否调整首层尺寸。
- lowerWall 首层相邻内部面：非正交角最大 5.871°、>70° 0 面；歪斜度最大 0.1141、>4 0 面；首层单元长宽比 P95 3.71。
**待补全的关键证据**

- 壁面 upperWall 缺少实际 yPlus；计算前估算还缺少正的 friction_velocity（或 wall_shear_stress、rho）
- 壁面 lowerWall 缺少实际 yPlus；计算前估算还缺少正的 friction_velocity（或 wall_shear_stress、rho）
- 缺少试算后各入口/出口的有符号质量通量，无法核对质量守恒
- 缺少压降、流量或换热量的监测序列，无法复核结果稳定性
- 缺少至少三套网格的同一目标量结果，无法检查网格敏感性

## 4. 质量指标

| 指标 | 极值 | 阈值（中等/高/致命） | 超标范围 | 等级 |
|---|---|---|---|---|
| 非正交性 | 最大 5.95° | > 65/70/85 | 0 | 🟢 可接受 |
| 歪斜度（OpenFOAM 定义） | 最大 0.2606 | > 2.5/4/20 | 0 | 🟢 可接受 |
| 长宽比 | 最大 8.141 | > 1000/10000/— | 0 | 🟢 可接受 |
| 单元行列式 | 最小 0.01299 | < 0.01/0.001/— | 0 | 🟢 可接受 |
| 面插值权重 | 最小 0.4003 | < 0.05/0.02/— | 0 | 🟢 可接受 |
| 相邻单元体积比 | 最小 0.6671 | < 0.01/0.001/— | 0 | 🟢 可接受 |
| 壁面 upperWall 的近壁内部面非正交角 | 最大 5.95° | — | 0 | 🟢 可接受 |
| 壁面 upperWall 的近壁内部面歪斜度 | 最大 0.1306 | — | 0 | 🟢 可接受 |
| 壁面 lowerWall 的近壁内部面非正交角 | 最大 5.871° | — | 0 | 🟢 可接受 |
| 壁面 lowerWall 的近壁内部面歪斜度 | 最大 0.1141 | — | 0 | 🟢 可接受 |

- **非正交性**：平均值 1.63°；分布：>50°: 0，>65°: 0，>70°: 0，>80°: 0；定义：面法向与相邻单元中心连线的夹角（仅内部面），0° 为理想
- **歪斜度（OpenFOAM 定义）**：分布：>1: 0，>2.5: 0，>4: 0，>10: 0；定义：面中心相对两单元中心连线交点的偏移，按面尺寸归一化；无上界，0 为理想
- **长宽比**：定义：OpenFOAM cellAspectRatio，1 为理想
- **壁面 upperWall 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 upperWall 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 lowerWall 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 lowerWall 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标

## 5. 问题定位

没有需要定位的问题，或输入不含位置信息。

## 6. 按优先级排列的网格优化建议

已评估指标无需修改；若关注压降或换热精度，继续检查 y⁺、近壁层和目标量的网格敏感性。

**下一步取证**

- 壁面 upperWall 缺少实际 yPlus；计算前估算还缺少正的 friction_velocity（或 wall_shear_stress、rho）
- 壁面 lowerWall 缺少实际 yPlus；计算前估算还缺少正的 friction_velocity（或 wall_shear_stress、rho）
- 缺少试算后各入口/出口的有符号质量通量，无法核对质量守恒
- 缺少压降、流量或换热量的监测序列，无法复核结果稳定性
- 缺少至少三套网格的同一目标量结果，无法检查网格敏感性
- 已有试算时，可用 OpenFOAM 的 `yPlus` 功能对象输出壁面场；提供该 ASCII 场用于逐壁面复核。

## 7. 局限与说明

- 位置/分布统计来自本工具按 OpenFOAM 公式的独立计算，数值可能与 checkMesh 有微小差别；严重程度以 checkMesh 数值为准。
- 二维网格（含 empty 面）：长宽比只在求解方向上计算。
- 阈值为经验值（见 `scripts/thresholds.json`），严重程度需结合求解类型判断：同样的指标对稳态 RANS 和瞬态多相/动网格计算的影响不同。

## 8. 检查日志

| 时间(s) | 状态 | 步骤 | 命令 |
|---|---|---|---|
| 0.0 | ok | 识别网格来源：openfoam / case（找到 constant/polyMesh/{points,faces,owner}；存在 system/controlDict） |  |
| 0.05 | ok | 使用已有 checkMesh 日志：/home/foamuser/OpenFOAM/foamuser-12/run/pitzDailySteady-mesh-quality-preflight/log.checkMesh |  |
| 0.05 | ok | 用 Python 读取 polyMesh，计算各面/单元指标分布和位置 | `polymesh.analyse(/home/foamuser/OpenFOAM/foamuser-12/run/pitzDailySteady-mesh-quality-preflight/constant/polyMesh)` |
| 0.6 | ok | polyMesh 读取完成：12225 个单元，49180 个面 |  |
