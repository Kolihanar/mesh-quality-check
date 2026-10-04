# 通用路线（Gmsh、VTK、CGNS、Abaqus .inp、ASCII Fluent .msh 等）

## 原理

用 meshio 读取网格，转换为 VTK 单元后用 VTK/Verdict 的质量指标逐单元计算。同一套定义适用于所有来源，因此可以横向比较不同网格生成器的结果，但**不能**与 Fluent 或 OpenFOAM 报告中的同名指标直接比较。

只评估最高维度的单元（3D 网格评估体单元，2D 网格评估面单元）；低一维的单元（Gmsh 的边界三角形等）用来定位"坏单元靠近哪个边界"。
二次单元只取角点评估。多边形/多面体单元不支持，会在报告中列出。

## 指标

| 指标 | 适用单元 | 理想值 | 本工具阈值（中等/高/致命） |
|---|---|---|---|
| 缩放雅可比 Scaled Jacobian | 全部 | 1 | <0.3 / <0.1 / ≤0（翻转） |
| 长宽比 | tri/quad/tet 用 aspect_ratio；hex/wedge 用 max_aspect_frobenius | 1 | >20 / >100 |
| 歪斜度 skew | quad/hex | 0 | >0.6 / >0.85 |
| 最小内角 | tri/quad/tet | 60°（三角形）/ 90°（四边形） | <20° / <10° |

体积（或面积）≤0、缩放雅可比 ≤0 的单元单独列为致命问题。

通用路线不计算非正交性和相邻单元尺寸比（增长率）。需要这两个指标时，转换为 OpenFOAM（`gmshToFoam`、`fluentMeshToFoam` 等）后用 checkMesh 检查。

## 输出的 VTU 文件

报告目录中的 `mesh_quality.vtu` 带有 scaled_jacobian、aspect_ratio、skew、min_angle 和体积字段。在 ParaView 中按字段着色，或用 Threshold 过滤出低于阈值的单元，就能直接看到问题区域。

## Gmsh 常用改进手段

- `Mesh.Optimize = 1;`（四面体优化），`Mesh.OptimizeNetgen = 1;`（Netgen 优化器，对狭长四面体效果明显）；
- 换三维算法：`Mesh.Algorithm3D = 10;`（HXT）或 `1;`（Delaunay），对比质量；
- 在尖角、薄层附近用尺寸场（Field）局部加密，避免尺寸突变；
- 检查几何：重复面、极短边、微小特征是低质量单元的常见来源，可在 CAD 中去除或用 `Geometry.Tolerance` 合并。
