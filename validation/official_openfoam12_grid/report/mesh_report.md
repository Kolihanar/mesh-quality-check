# 网格质量检查报告

- 生成时间：2026-10-04 19:00:00
- 输入：`/home/foamuser/OpenFOAM/foamuser-12/run/pitzDailySteady-grid-fine-monitored-20261004`
- 识别结果：**OpenFOAM**（case）——找到 constant/polyMesh/{points,faces,owner}；存在 system/controlDict

## 结论：🔴 高风险

已检查指标存在高风险偏离；需结合实际边界条件及目标量验证其影响。

CFD 适用性判断：**高风险指标待复核**。

checkMesh 自身结论：`Mesh OK`

## 1. 网格基本信息

| 项目 | 值 |
|---|---|
| 单元数 | 27703 |
| 面数 | 111233 |
| 内部面数 | 54985 |
| 节点数 | 56250 |
| 维度 | 2D |
| OpenFOAM 版本 | 12 |
| 单元类型 | hexahedra 27703 |
| 包围盒 | [-0.0206, -0.0254, -0.0005] → [0.29, 0.0254, 0.0005] |
| 单元体积 | 最小 7.297e-11，最大 1.713e-09 |
| 边界 | inlet[patch](45)，outlet[patch](86)，upperWall[wall](335)，lowerWall[wall](376)，frontAndBack[empty](55406) |

## 2. 致命/拓扑问题

本次已执行的检查中未报告致命拓扑问题；未执行的检查见局限与说明。


## 3. CFD 适用性与近壁检查

当前范围：OpenFOAM 单相 RANS 内流。计算前 y⁺ 为估算，已有试算的 yPlus 场为求解后证据。

算例识别：求解器 foamRun；湍流类型 RAS；模型 kEpsilon。

| 壁面 | 首层中心距：最小/中位/P95 | y⁺ 证据 | y⁺：P05/中位/P95 | 目标 | 区间外面积 |
|---|---|---|---|---|---|
| upperWall | 5.548e-05/1.238e-04/1.452e-04 | solver_result | 1.668/3.78/5.531 | [30.0, 300.0] | 100.0% |
| lowerWall | 1.033e-04/3.365e-04/3.661e-04 | solver_result | 1.295/12.5/16.32 | [30.0, 300.0] | 100.0% |

表中 y⁺ 目标是所选工况的筛查区间，区间外比例表示目标偏离，并不单独证明求解失败或结果不可靠。首层中心距按单元中心到边界面平面的法向投影计算。近壁层数与覆盖率需要实际生成记录或可识别的层字段；规则六面体的连续排列不直接算作边界层。

- upperWall 壁面场类型：nut=nutkWallFunction、omega=omegaWallFunction、epsilon=epsilonWallFunction
- upperWall：OpenFOAM 12 的 nutkWallFunction / epsilonWallFunction 含低 y⁺ 分支；低于筛查下限时先核对实际分支、壁面剪切及压降/换热的网格敏感性，再决定是否调整首层尺寸。
- upperWall 首层相邻内部面：非正交角最大 5.961°、>70° 0 面；歪斜度最大 0.1306、>4 0 面；首层单元长宽比 P95 7.183。
- lowerWall 壁面场类型：nut=nutkWallFunction、omega=omegaWallFunction、epsilon=epsilonWallFunction
- lowerWall：OpenFOAM 12 的 nutkWallFunction / epsilonWallFunction 含低 y⁺ 分支；低于筛查下限时先核对实际分支、壁面剪切及压降/换热的网格敏感性，再决定是否调整首层尺寸。
- lowerWall 首层相邻内部面：非正交角最大 5.908°、>70° 0 面；歪斜度最大 0.1154、>4 0 面；首层单元长宽比 P95 3.761。
**已有试算的复核结果**

- 恒密度流体积通量相对不平衡：0.0041%；容差 1.00%
- kinematic_pressure_difference_m2_s2_coarse 末段漂移：2.03%；容差 0.50%
- kinematic_pressure_difference_m2_s2_medium 末段漂移：6.49%；容差 0.50%
- kinematic_pressure_difference_m2_s2_fine 末段漂移：8.21%；容差 0.50%
- kinematic_pressure_difference_m2_s2 细/中网格变化：12.80%；容差 2.00%
  - 相关监测量末段仍在漂移：kinematic_pressure_difference_m2_s2_coarse、kinematic_pressure_difference_m2_s2_medium、kinematic_pressure_difference_m2_s2_fine；当前网格差异只是初步比较，先使各套网格的目标量稳定，再判断网格敏感性。

## 4. 质量指标

| 指标 | 极值 | 阈值（中等/高/致命） | 超标范围 | 等级 |
|---|---|---|---|---|
| 非正交性 | 最大 5.961° | > 65/70/85 | 0 | 🟢 可接受 |
| 歪斜度（OpenFOAM 定义） | 最大 0.261 | > 2.5/4/20 | 0 | 🟢 可接受 |
| 长宽比 | 最大 8.303 | > 1000/10000/— | 0 | 🟢 可接受 |
| 单元行列式 | 最小 0.01173 | < 0.01/0.001/— | 0 | 🟢 可接受 |
| 面插值权重 | 最小 0.4002 | < 0.05/0.02/— | 0 | 🟢 可接受 |
| 相邻单元体积比 | 最小 0.6669 | < 0.01/0.001/— | 0 | 🟢 可接受 |
| 壁面 upperWall 的近壁内部面非正交角 | 最大 5.961° | — | 0 | 🟢 可接受 |
| 壁面 upperWall 的近壁内部面歪斜度 | 最大 0.1306 | — | 0 | 🟢 可接受 |
| 壁面 upperWall 的 y⁺ 区间偏离 |  5.531 | — | 335 个壁面面（100%，大面积） | 🔴 高风险 |
| 壁面 lowerWall 的近壁内部面非正交角 | 最大 5.908° | — | 0 | 🟢 可接受 |
| 壁面 lowerWall 的近壁内部面歪斜度 | 最大 0.1154 | — | 0 | 🟢 可接受 |
| 壁面 lowerWall 的 y⁺ 区间偏离 |  16.32 | — | 376 个壁面面（100%，大面积） | 🔴 高风险 |
| 稳态质量守恒 |  4.055e-05 | — | 未知（只有极值） | 🟢 可接受 |
| 监测量 kinematic_pressure_difference_m2_s2_coarse 的末段漂移 |  0.02031 | — | 未知（只有极值） | 🔴 高风险 |
| 监测量 kinematic_pressure_difference_m2_s2_medium 的末段漂移 |  0.06486 | — | 未知（只有极值） | 🔴 高风险 |
| 监测量 kinematic_pressure_difference_m2_s2_fine 的末段漂移 |  0.08208 | — | 未知（只有极值） | 🔴 高风险 |
| 目标量 kinematic_pressure_difference_m2_s2 的网格敏感性 |  0.128 | — | 未知（只有极值） | 🔴 高风险 |

- **非正交性**：平均值 1.683°；分布：>50°: 0，>65°: 0，>70°: 0，>80°: 0；定义：面法向与相邻单元中心连线的夹角（仅内部面），0° 为理想
- **歪斜度（OpenFOAM 定义）**：分布：>1: 0，>2.5: 0，>4: 0，>10: 0；定义：面中心相对两单元中心连线交点的偏移，按面尺寸归一化；无上界，0 为理想
- **长宽比**：定义：OpenFOAM cellAspectRatio，1 为理想
- **壁面 upperWall 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 upperWall 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 upperWall 的 y⁺ 区间偏离**：定义：筛查目标区间 30.0–300.0（工况显式指定）；按面积计算区间外比例 100.0%；证据 solver_result；单凭偏离不能判定求解失败
- **壁面 lowerWall 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 lowerWall 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 lowerWall 的 y⁺ 区间偏离**：定义：筛查目标区间 30.0–300.0（工况显式指定）；按面积计算区间外比例 100.0%；证据 solver_result；单凭偏离不能判定求解失败
- **稳态质量守恒**：定义：恒密度不可压缩流：各边界体积通量按外法向有符号求和，除以较大的流入/流出总量
- **监测量 kinematic_pressure_difference_m2_s2_coarse 的末段漂移**：定义：比较末尾两个等长窗口的均值；监测量稳定不单独证明网格无关
- **监测量 kinematic_pressure_difference_m2_s2_medium 的末段漂移**：定义：比较末尾两个等长窗口的均值；监测量稳定不单独证明网格无关
- **监测量 kinematic_pressure_difference_m2_s2_fine 的末段漂移**：定义：比较末尾两个等长窗口的均值；监测量稳定不单独证明网格无关
- **目标量 kinematic_pressure_difference_m2_s2 的网格敏感性**：定义：细/中网格目标量相对变化；需要同一物理模型和边界条件，未据此推断严格误差界；相关监测量末段仍在漂移，网格敏感性比较暂为初步结果，需先使各网格目标量稳定

## 5. 问题定位

**壁面 upperWall 的 y⁺ 区间偏离**
- 靠近边界：upperWall（335）
- 包围盒：[-0.02007196131, 0.01677649874, 0.0] → [0.28831523929999997, 0.025400000000000002, 0.0]

**壁面 lowerWall 的 y⁺ 区间偏离**
- 靠近边界：lowerWall（376）
- 包围盒：[-0.020071961309999997, -0.025400000000000002, 0.0] → [0.2883152393, 0.0, 0.0]

可视化：checkMesh 会把坏面/坏单元写成集合（如 nonOrthoFaces、skewFaces）。用 `foamToVTK -faceSet nonOrthoFaces`（单元集合用 -cellSet）转成 VTK，或 ESI 版直接用 `checkMesh -allGeometry -allTopology -writeSets vtk`，在 ParaView 中查看。

## 6. 按优先级排列的网格优化建议

1. **监测量 kinematic_pressure_difference_m2_s2_coarse 的末段漂移**（高风险）
   - 位置：对应的监测目标量及影响区域
   - 证据：极值 0.02030929163706181；比较末尾两个等长窗口的均值；监测量稳定不单独证明网格无关
   - 修改：先检查残差停止条件、边界条件和数值设置，并继续迭代至目标量稳定；若仍持续漂移，再定位相关壁面或强梯度区域并调整局部网格。
   - 验证：重新检查目标量监测序列，确认末段变化低于容差后再比较不同网格。
2. **监测量 kinematic_pressure_difference_m2_s2_medium 的末段漂移**（高风险）
   - 位置：对应的监测目标量及影响区域
   - 证据：极值 0.06485700276453174；比较末尾两个等长窗口的均值；监测量稳定不单独证明网格无关
   - 修改：先检查残差停止条件、边界条件和数值设置，并继续迭代至目标量稳定；若仍持续漂移，再定位相关壁面或强梯度区域并调整局部网格。
   - 验证：重新检查目标量监测序列，确认末段变化低于容差后再比较不同网格。
3. **监测量 kinematic_pressure_difference_m2_s2_fine 的末段漂移**（高风险）
   - 位置：对应的监测目标量及影响区域
   - 证据：极值 0.08207941570109276；比较末尾两个等长窗口的均值；监测量稳定不单独证明网格无关
   - 修改：先检查残差停止条件、边界条件和数值设置，并继续迭代至目标量稳定；若仍持续漂移，再定位相关壁面或强梯度区域并调整局部网格。
   - 验证：重新检查目标量监测序列，确认末段变化低于容差后再比较不同网格。
4. **目标量 kinematic_pressure_difference_m2_s2 的网格敏感性**（高风险）
   - 位置：对应的监测目标量及影响区域
   - 证据：极值 0.12803870842636536；细/中网格目标量相对变化；需要同一物理模型和边界条件，未据此推断严格误差界；相关监测量末段仍在漂移，网格敏感性比较暂为初步结果，需先使各网格目标量稳定
   - 修改：先使各套网格上的目标量监测序列稳定，再重新比较细/中结果；若变化仍超容差，定位壁面、分离区和强梯度区后局部加密，保持物理模型与边界条件一致。
   - 验证：各套目标量末段变化先低于容差，再比较细/中网格差异；必要时增加更细网格。
5. **壁面 upperWall 的 y⁺ 区间偏离**（高风险）
   - 位置：壁面 upperWall
   - 证据：极值 5.531；范围 335 / 335；筛查目标区间 30.0–300.0（工况显式指定）；按面积计算区间外比例 100.0%；证据 solver_result；单凭偏离不能判定求解失败
   - 修改：壁面 upperWall 的 y⁺ 低于所设筛查下限；先核对当前 nutkWallFunction / epsilonWallFunction 的低 y⁺ 分支是否符合关注的壁面剪切、压降或换热目标。若需要把首层置于对数区，再按实际 y⁺ 分布增大首层法向距离，同时检查尺寸过渡与局部流动分辨率；不要仅为满足区间而直接放粗网格。
   - 验证：重新计算该壁面 yPlus，并比较壁面剪切、压降/换热量及其网格敏感性。
6. **壁面 lowerWall 的 y⁺ 区间偏离**（高风险）
   - 位置：壁面 lowerWall
   - 证据：极值 16.325；范围 376 / 376；筛查目标区间 30.0–300.0（工况显式指定）；按面积计算区间外比例 100.0%；证据 solver_result；单凭偏离不能判定求解失败
   - 修改：壁面 lowerWall 的 y⁺ 低于所设筛查下限；先核对当前 nutkWallFunction / epsilonWallFunction 的低 y⁺ 分支是否符合关注的壁面剪切、压降或换热目标。若需要把首层置于对数区，再按实际 y⁺ 分布增大首层法向距离，同时检查尺寸过渡与局部流动分辨率；不要仅为满足区间而直接放粗网格。
   - 验证：重新计算该壁面 yPlus，并比较壁面剪切、压降/换热量及其网格敏感性。

## 7. 局限与说明

- 位置/分布统计来自本工具按 OpenFOAM 公式的独立计算，数值可能与 checkMesh 有微小差别；严重程度以 checkMesh 数值为准。
- 二维网格（含 empty 面）：长宽比只在求解方向上计算。
- 阈值为经验值（见 `scripts/thresholds.json`），严重程度需结合求解类型判断：同样的指标对稳态 RANS 和瞬态多相/动网格计算的影响不同。

## 8. 检查日志

| 时间(s) | 状态 | 步骤 | 命令 |
|---|---|---|---|
| 0.0 | ok | 识别网格来源：openfoam / case（找到 constant/polyMesh/{points,faces,owner}；存在 system/controlDict） |  |
| 0.03 | ok | 使用已有 checkMesh 日志：/home/foamuser/OpenFOAM/foamuser-12/run/pitzDailySteady-grid-fine-monitored-20261004/log.checkMesh |  |
| 0.04 | ok | 用 Python 读取 polyMesh，计算各面/单元指标分布和位置 | `polymesh.analyse(/home/foamuser/OpenFOAM/foamuser-12/run/pitzDailySteady-grid-fine-monitored-20261004/constant/polyMesh)` |
| 1.15 | ok | polyMesh 读取完成：27703 个单元，111233 个面 |  |
