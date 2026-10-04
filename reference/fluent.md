# Fluent 网格指标

## 获取检查数据

TUI 命令（Fluent 求解器模式）：

```
/mesh/check        ; 体积、面积、拓扑检查，负体积会在这里报错
/mesh/quality      ; 最小正交质量、最大歪斜度、最大长宽比及最差单元位置
/mesh/size         ; 单元/面/节点数
```

批处理：脚本在报告目录生成 `fluent_mesh_check.jou`，运行
`fluent 3ddp -g -t1 -i fluent_mesh_check.jou`（二维改 `2ddp`），再把生成的 `.trn` 交给本工具。

## 指标定义与经验范围

Fluent 的指标都在 0–1 之间，**与 OpenFOAM 的同名指标定义不同，不能直接比较。**

正交质量（Orthogonal Quality，越大越好）：

| 范围 | 评价 |
|---|---|
| < 0.001 | 不可接受（本工具：致命） |
| 0.001–0.01 | 很差，Fluent 建议最小值 > 0.01（本工具：高风险） |
| 0.01–0.1 | 差（本工具：中等） |
| 0.1–0.2 | 可接受 |
| > 0.2 | 好 |

歪斜度（Skewness / Ortho Skew，越小越好）：

| 范围 | 评价 |
|---|---|
| > 0.98 | 不可接受（本工具：高风险） |
| 0.95–0.98 | 差（本工具：中等） |
| 0.8–0.95 | 可接受 |
| < 0.8 | 好 |

以上是 ANSYS 常用的经验表，不同版本文档表述略有差异。少量单元超标时求解器通常仍能运行，所以本工具把歪斜度 >0.98 定为"高风险"而不是"致命"。

## 只有极值的局限

`/mesh/quality` 只报告最差的一个单元，无法得知有多少单元超标。判断影响范围的办法：
- Fluent 中显示 Orthogonal Quality 的云图或直方图（Results > Graphics > Contours，Mesh 类别下的 Orthogonal Quality）；
- 导出为 CGNS 或 ASCII .msh，用本工具的通用路线统计（指标定义会变为 VTK 定义）。

## 常见修复

- `mesh/repair-improve/improve-quality`：对多面体网格最有效；
- `mesh/polyhedra/convert-domain`：四面体转多面体，通常显著改善歪斜度；
- 负体积：在网格软件（Fluent Meshing / ICEM / Workbench Meshing）中修复；动网格算例若运动后才出现，属于网格变形问题（检查 smoothing/remeshing、时间步、运动边界附近的网格余量）；
- 暂时无法改网格：一阶格式 + 较小松弛因子起算，稳定后再切换高阶格式；使用双精度求解器。
