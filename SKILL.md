---
name: mesh-quality-check
description: CFD 网格质量与算例适用性检查。识别 OpenFOAM、Fluent、Gmsh 或通用网格格式，计算或解析质量指标，输出 Markdown 和 JSON 报告。对 OpenFOAM 单相 RANS 内流还能结合壁面处理、首层距离、估算或实际 yPlus、边界层实测数据与已有试算结果判断是否适合当前用途，并给出具体优化建议。当用户要求检查网格质量、y+、边界层网格、网格引起的发散或 CFD 计算适用性时使用。
---

# 网格质量检查

## 核心原则

- **工具提供事实，你负责解释。** 所有数值都来自脚本输出，不要自己编造、估算或"补全"任何网格统计量。
- **不跨软件换算数值。** OpenFOAM 的 skewness、Fluent 的 skewness、VTK 的 skew 是三个不同的量，只比较严重程度等级。
- **区分检查层级。** 基础质量检查回答网格几何和拓扑是否有明显问题；OpenFOAM 单相 RANS 内流的适用性检查还结合近壁证据与已有试算结果。目标量精度需要多套网格结果验证。
- **核对 y⁺ 目标与真实壁面函数。** 30–300 等区间是工况筛查目标，不是所有 OpenFOAM 壁面函数的硬性有效区间。若报告显示 y⁺ 区间偏离，结合 `0/nut`、`0/epsilon` 等边界条件和目标量解释；低 y⁺ 本身不证明发散，求解收敛也不证明目标量准确。
- **核对通量单位。** OpenFOAM `phi` 的量纲为 `[0 3 -1 0 0 0 0]` 时是体积通量；确认恒密度并设置 `flow.constant_density: true` 后，可用 `volumetric_flux_m3_s` 核对相对守恒，不能将其直接填入 `mass_flux_kg_s`。
- **先核对目标量稳定性。** 求解器达到残差停止条件后，压力差或换热量仍可能漂移或往复波动。比较末段均值和 P05–P95 跨度；三网格末次值若来自不稳定的目标量，只作初步敏感性比较，先稳定各套算例。
- **致命问题优先。** 一旦出现致命等级，结论就是"先修网格，不要开始计算"，不要再讨论次要指标的细节。

## 流程

### 1. 确认输入

需要以下之一：OpenFOAM 算例目录、checkMesh 日志、Fluent 网格/算例文件或 transcript、其他网格文件。
用户只贴了文本时，先把文本存成文件再处理。什么都没有时，告诉用户需要提供什么（见第 5 步的命令）。

### 2. 运行检查

```bash
python -m pip install -r requirements.txt   # 在本 Skill 目录和项目虚拟环境中首次使用
python <本 Skill 目录>/scripts/mesh_check.py <路径> -o <报告目录>
```

常用参数：
- `--checkmesh-log log.checkMesh`：OpenFOAM 算例已经有 checkMesh 输出时使用，避免重跑，同时仍能得到位置统计；
- `--force-source openfoam|fluent|generic`：自动识别出错时手动指定。
- `--context cfd_context.json`：提供工况、壁面处理、实测层数据和已有试算摘要；格式见 `reference/cfd_openfoam.md`。
- `--yplus-field <时间目录/yPlus>`：读取已有试算的 ASCII yPlus 场；未指定时自动寻找最新时间目录中的 yPlus。
- `--layer-field <时间目录/nSurfaceLayers>`：读取 snappyHexMesh 实际加层的 ASCII 边界场；未指定时自动寻找。报告给出逐壁面面积加权覆盖率、低于目标的面积比例与位置。

脚本会自动：识别来源 → 调用对应适配器（OpenFOAM 有 checkMesh 时会自动运行）→ 分级 → 写出
`mesh_report.md`、`mesh_report.json`，以及视情况生成的 `log.checkMesh`、`fluent_mesh_check.jou`、`mesh_quality.vtu`。
退出码：0 = 已评估质量可接受/中等，2 = 高风险/致命，3 = 没有可用检查数据。`overall` 是已执行指标的等级；当前工况能否使用还要读取 `readiness` 和 `cfd.missing`。

### 3. 阅读报告并结合场景解释

读 `mesh_report.json`（结构化）或 `mesh_report.md`。然后读对应的参考文档，用来解释和补充建议：
- 总体判断原则：`reference/common.md`（每次都读）
- OpenFOAM：`reference/openfoam.md`
- Fluent：`reference/fluent.md`
- Gmsh / 通用格式：`reference/generic.md`
- OpenFOAM 单相 RANS 内流适用性：`reference/cfd_openfoam.md`（有算例目录时读）
- 使用 OpenFOAM 官方教程验证本 Skill：`reference/official_validation.md`（需要验证时读）

结合用户的计算类型调整解释（不要改动报告里的等级，而是在解释中说明）：
- 不知道计算类型且会影响结论时，问一句；
- 稳态 RANS 对少量零星的坏单元容忍度较高；瞬态、多相（VoF 界面）、LES、动网格对同样的问题更敏感；
- 坏单元的**位置**和**数量**比极值更重要：零星分布在远离关注区的坏单元，通常比大面积分布在壁面或界面附近的问题轻。

### 4. 向用户汇报

简洁地给出：
1. 识别结果和总体结论（等级 + 能否开始计算）；
2. 最重要的 1–3 个问题：数值、范围（数量/占比）、位置；
3. 按优先级给出问题位置、证据、具体网格修改动作和验证方式；
4. 区分计算前 y⁺ 估算与试算后真实 yPlus，说明实测层数据的来源；
5. 会影响结论的待补全证据，以及补全信息需要运行的命令；
6. 报告文件位置。

不要把整份报告贴进对话。

### 5. 信息不足时

明确说出缺什么、怎么获取：
- OpenFOAM：在算例目录运行 `checkMesh -allGeometry -allTopology > log.checkMesh`；
- OpenFOAM 12 的 `incompressibleFluid` 已有试算：`foamPostProcess -solver incompressibleFluid -func yPlus -latestTime > log.yPlus`；随后检查时间目录的 ASCII `yPlus` 场。
- Fluent：在 TUI 中依次执行 `/mesh/check`、`/mesh/quality`、`/mesh/size`，把输出（或 transcript 文件）交给本工具；也可以用报告目录里生成的 journal 批处理运行；
- 二进制 polyMesh 无法定位坏单元：`foamFormatConvert`（controlDict 里 `writeFormat ascii`）后重新检查。

## 超出 v1 范围的情况

- **动网格**：本工具只检查静态网格（当前时刻）。怀疑运动导致畸变时，分别检查初始时刻和发散前最后一个时间步的网格并对比；OpenFOAM 可用 `moveDynamicMesh -checkMeshQuality`。
- **重叠网格（overset）**：不检查 orphan/donor，请让用户提供求解器的重叠网格连通性报告。
- **网格敏感性**：可对用户提供的三套网格目标量比较细/中结果变化；若要严格估计离散误差，还需要受控细化序列及更多计算证据。

## 规则

- 绝不在没有运行脚本或没有用户提供数据的情况下给出网格质量结论。
- 不仅凭单个极值判断网格好坏，必须看超标数量、占比和位置；Fluent 只有极值时要明确说明"无法判断影响范围"。
- 引用阈值时说明它来自哪个软件、是经验值。
- 改动用户网格或算例设置之前先征得同意；本 Skill 本身只读，不修改输入文件（checkMesh 可能会在算例里写入 cellSet，这是 OpenFOAM 的正常行为）。
