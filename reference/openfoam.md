# OpenFOAM 网格指标

## checkMesh 输出中的关键项

| checkMesh 输出 | 含义 | 默认报警 | 本工具等级 |
|---|---|---|---|
| `Zero or negative cell volume detected` | 负/零体积单元 | 任何 | 致命 |
| `Error in face pyramids` | 面朝向错误或单元严重扭曲 | 任何 | 致命 |
| `Zero or negative face area` | 退化面 | 任何 | 致命 |
| `Open cells found` / boundary openness 失败 | 单元或边界不封闭 | 任何 | 致命 |
| `Number of regions: N` (N>1) | 多个不连通区域 | N>1 | 高风险（多区域 CHT 拆分前属正常） |
| `Mesh non-orthogonality Max` | 非正交角（度） | >70° 计数 | 中等 >65，高 >70，致命 >85 |
| `Max skewness` | OpenFOAM 歪斜度（无上界） | >4 | 中等 >2.5，高 >4，致命 >20 |
| `Max aspect ratio` | 长宽比 | >1000 | 中等 >1000，高 >10000 |
| `Cell determinant` | 单元在某方向是否退化 | <0.001 | 中等 <0.01，高 <0.001 |
| `Face interpolation weight` | 相邻单元尺寸差 | <0.05 | 中等 <0.05，高 <0.02 |
| `Face volume ratio` | 相邻单元体积比 | <0.01 | 中等 <0.01，高 <0.001 |
| `Concave cells` | 凹单元 | 任何 | 中等 |
| `Error in face tets` | 面四面体分解差 | 任何 | 中等（影响粒子追踪） |

注意：checkMesh 对非正交性超过 70° 只标记 `*`（警告），不计入 "Failed N mesh checks"；本工具仍按高风险处理，因为它对求解稳定性影响很大。

## 指标与数值设置的对应关系

暂时无法改网格时，可以通过数值设置换取稳定性：

| 网格最大非正交角 | laplacianSchemes / snGradSchemes | nNonOrthogonalCorrectors |
|---|---|---|
| < 50° | `Gauss linear corrected` / `corrected` | 0 |
| 50–70° | `Gauss linear corrected` / `corrected` | 1–2 |
| 70–80° | `Gauss linear limited corrected 0.5` / `limited corrected 0.5` | 2–3 |
| > 80° | `Gauss linear limited corrected 0.33` / `limited corrected 0.33` | 3+，且应尽快修网格 |

高歪斜度时：
- gradSchemes 用 `cellLimited Gauss linear 1`；
- 对流项用有界格式（如 `bounded Gauss linearUpwind grad(U)`，或 `limitedLinearV 1`）；
- 插值可考虑 `skewCorrected linear`（代价较高）。

大长宽比（非边界层）时：压力求解用 GAMG，检查边界层增长率（一般 ≤1.2）。

## snappyHexMesh 质量控制

`system/meshQualityDict`（或 snappyHexMeshDict 中的 meshQualityControls）里的常用参数：
`maxNonOrtho 65`、`maxBoundarySkewness 20`、`maxInternalSkewness 4`、`maxConcave 80`、`minVol 1e-13`、
`minTetQuality 1e-15`（不少教程用 -1e30 关闭）、`minDeterminant 0.001`、`minFaceWeight 0.05`、`minVolRatio 0.01`、
`nSmoothScale 4`、`errorReduction 0.75`。收紧这些参数后重新运行 snappyHexMesh，它会在贴体和加层阶段回退不合格的位移。

## 版本差异

- checkMesh 发现问题时会把坏面/坏单元写成集合（nonOrthoFaces、skewFaces、highAspectRatioCells 等，通常在 `constant/polyMesh/sets/`）。
- 可视化：ESI 版（v2xxx）可用 `checkMesh -writeSets vtk` 直接输出 VTK；通用做法是 `foamToVTK -faceSet nonOrthoFaces`（单元集合用 `-cellSet`）。具体选项以所用版本的 `checkMesh -help` 为准。
- ESI 版支持 `checkMesh -writeFields '(nonOrthoAngle skewness cellAspectRatio)'` 写出逐单元指标场，便于在 ParaView 中着色查看；Foundation 版是否支持取决于版本。
- Foundation 版 v11 起求解器改为 `foamRun -solver ...` 模块形式，但 checkMesh 用法基本不变。

## 本工具的独立计算

当算例是 ASCII 格式时，脚本会用 Python 按 OpenFOAM 的公式重新计算非正交性、歪斜度和长宽比，用来给出分布和位置。
数值可能与 checkMesh 有微小差别（例如单元中心算法细节），严重程度以 checkMesh 的数值为准。
